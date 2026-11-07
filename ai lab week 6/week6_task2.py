import re
def word_spans(text):
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
def windows(text, size=40, overlap=10, offset=0):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    spans = word_spans(text)
    result = []
    for i in range(0, len(spans), size - overlap):
        j = min(i + size, len(spans))
        result.append((offset + spans[i][0], offset + spans[j - 1][1]))
        if j == len(spans):
            break
    return result
def sentence_chunks(text, size=40):
    if size <= 0:
        raise ValueError("size must be positive")
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?]\s+", text)] + [len(text)]
    out = []
    pending = None
    count = 0
    for a, b in zip(cuts, cuts[1:]):
        segment = text[a:b]
        n = len(segment.split())
        if not n:
            continue
        if n > size:
            if pending is not None:
                out.append(pending)
            out.extend(windows(segment, size, 0, a))
            pending = None
            count = 0
        elif pending is not None and count + n <= size:
            pending = (pending[0], b)
            count = count + n

        else:
            if pending is not None:
                out.append(pending)
            pending = (a, b)
            count = n
    if pending is not None:
        out.append(pending)
    return out
def make_chunks(docs, strategy):
    result = []
    for doc_id, text in docs.items():
        if strategy == "sentence":
            spans = sentence_chunks(text)
        else:
            spans = windows(text, 40, int(strategy))
        for i, (a, b) in enumerate(spans):
            result.append({
                "id": f"{doc_id}:{i}",
                "doc": doc_id,
                "start": a,
                "end": b,
                "text": text[a:b]
            })
    return result
if _name_ == "_main_":
    assert windows("") == []
    assert windows("short text") == [(0, 10)]
    try:
        windows("a b", 2, 2)
    except ValueError:
        print("Invalid overlap test passed")
    else:
        raise AssertionError("Invalid overlap was accepted")
    long = " ".join(["word"] * 95) + "."
    assert all(
        len(long[a:b].split()) <= 40
        for a, b in sentence_chunks(long)
    )
    print("Long sentence test passed")
    docs = {
        "example": """ Groundwork for AI: 1900-1950
In the early 1900s, there was a lot of media created that centered around 
the idea of artificial humans.
 So much so that scientists of all sorts started asking the question:
  is it possible to create an artificial brain? 
 Some creators even made some versions of what we now call “robots” 
 (and the word was coined in a Czech play in 1921) though most of them were relatively simple.
  These were steam-powered for the most part,
 and some could make facial expressions and even walk.
 The idea of “artificial intelligence” goes back thousands of years, to ancient philosophers 
 considering questions of life and death. In ancient times, inventors made things called “automatons”
  which were mechanical and moved independently of human intervention. The word “automaton” comes
   from ancient Greek, and means “acting of one’s own will.” One of the earliest records of an automaton
    comes from 400 
   BCE and refers to a mechanical pigeon created by a friend of the philosopher Plato. Many years later,
  one of the most famous automatons was created by Leonardo da Vinci around the year 1495""",
      "example2":"""This range of time was when the interest in AI really came to a head. 
      Alan Turing published his work “Computer Machinery and Intelligence”
       which eventually became The Turing Test, which experts used to measure computer intelligence.
        The term “artificial intelligence”
       was coined and came into popular use.
       The idea of “artificial intelligence” goes back thousands of years, to ancient philosophers considering
        questions of life and death. In ancient times, inventors made things called “automatons” which were mechanical
         and moved independently of human intervention. The word “automaton” comes from ancient Greek, 
         and means “acting of one’s own will.” One of the earliest records of an automaton comes from 400 BCE
          and refers to a mechanical pigeon created by a friend of the philosopher Plato. Many years later, 
          one of the most famous automatons was created by Leonardo da Vinci around the year 1495 n the early 1900s, 
          there was a lot of media created that centered around the idea of artificial humans. 
          So much so that scientists of all sorts started asking the question: is it possible to create an artificial brain? 
          Some creators even made some versions of what we now call “robots” (and the word was coined in a Czech play in 1921)
           though most of them were relatively simple. These were steam-powered for the most part,
           and some could make facial expressions and even walk.""",
        "example3" : """The time between when the phrase “artificial intelligence” 
        was created, and the 1980s was a period of both rapid growth and struggle for AI research.
         The late 1950s through the 1960s was a time of creation. 
         From programming languages that are still in use to this day to books and 
         films that explored the idea of robots, AI became a mainstream idea quickly.
The 1970s showed similar improvements, such as the first anthropomorphic robot being built in Japan, 
to the first example of an autonomous vehicle being built by an engineering grad student. However, 
it was also a time of struggle for AI research, as the U.S. 
government showed little interest in continuing to fund AI research.The idea of “artificial intelligence” goes back thousands
 of years, to ancient
 philosophers considering questions of life and death. In ancient times, inventors made things called “automatons”
  which were mechanical and
  moved independently of human intervention. The word “automaton” comes from ancient Greek, and means “acting 
  of one’s own will.” One of the earliest records of an automaton comes from 400 BCE and refers to a mechanical 
  pigeon created by a friend of the philosopher Plato. Many years later, one of the most famous 
automatons was created by Leonardo da Vinci around the year 1495"""
    }
    for strategy in ["0", "10", "sentence"]:
        chunks = make_chunks(docs, strategy)
        print("\nStrategy:", strategy)
        for c in chunks:
            assert c["text"] == docs[c["doc"]][c["start"]:c["end"]]
            print(c)