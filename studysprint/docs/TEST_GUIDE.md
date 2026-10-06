# Manual test guide — Computer Networks lecture

Test file: [`sample_data/networks-lecture.pdf`](../sample_data/networks-lecture.pdf). It has 5 pages: OSI model, TCP/UDP, IP addressing, DNS, routing. To regenerate it, run `python backend/scripts/make_test_pdf.py`.

Live app: https://studysprint-6ufj.onrender.com. If it has been idle, give it about 1 minute to wake up.

## 1. Upload and topics

1. Log in as `demo` / `demopass123`, or create your own account.
2. On **Courses**, add "Computer Networks" with an exam date about 2 weeks away.
3. Upload `networks-lecture.pdf`.

**Expected**
- The message reads: "networks-lecture.pdf: 5 pages, 5 new topics".
- The topics are **The OSI Model** (p.1), **TCP and UDP** (p.2), **IP Addressing and Subnets** (p.3), **DNS Resolution** (p.4) and **Routing** (p.5).
- A study plan appears that ends with a **review** day.

## 2. Study session: test the grader

Click **Start today's session**. For each question you get, use the answers below to try a strong, a partial and a wrong answer. Each session question is different, so spread these across sessions.

Scores below come from the offline grader, which only gives credit for the key terms it's looking for. With an OpenAI or Groq key set, paraphrases also get credit.

| Question | Strong answer (5) | Partial answer (1–2) | Wrong answer (0) |
|---|---|---|---|
| What is the OSI model? | It's a seven layer framework that describes how data moves across a network | A framework that describes networking | I don't know |
| What is TCP? | A connection oriented protocol that guarantees reliable, ordered delivery | TCP is reliable and uses connections | It's a type of cable |
| What is UDP? | A connectionless protocol that sends datagrams without guaranteeing delivery | UDP is connectionless and sends datagrams | no idea |
| What is an IP address? | A numeric label that identifies a device on a network | A numeric label for a computer | A website name |
| What is DNS? | A distributed system that translates domain names into IP addresses | A system that translates names | It encrypts traffic |
| What is a router? | A device that forwards packets between networks using a routing table | A device that forwards data | A type of firewall |
| What is meant by "encapsulation"? | Each layer wraps the data from the layer above with its own header | Adding headers | Compressing files |
| Fill in: "three way _____" (TCP) | handshake: TCP performs it with SYN, SYN-ACK and ACK segments | handshake | timeout |

Vague answers like "UDP is fast" or "DNS finds websites" score 0 offline, because they contain none of the key terms.

**Check after each answer**
- The score out of 5 and its label.
- The **Missing** key points listed for anything below 5.
- **Source (page N)** shows the original sentence from the PDF.
- The topic mastery bar updates.

After the session, go back to the course page. Topics you answered badly have low mastery and appear near the top of tomorrow's plan.

## 3. Ask your material (RAG)

| Ask | Expected answer contains | Cited page |
|---|---|---|
| What does DNS do? | translates domain names into IP addresses | 4 |
| Why do games use UDP? | low latency matters more than retransmitting lost packets | 2 |
| What is NAT? | many devices share a single public IP address | 3 |
| How does Dijkstra's algorithm help routing? | computes the shortest path | 5 |
| What is photosynthesis? | "couldn't find this in your uploaded material" | none |

Ask the same question twice: the second answer is marked **(cached)**.

## 4. Study agent

| Goal | Expected intent and steps |
|---|---|
| Get me ready for the exam | `prepare`: curriculum_worker, quiz_worker (generates questions), planner_worker |
| quiz me | `quiz`: picks 5 questions, weakest topics first |
| make a study schedule | `plan`: planner_worker |
| What is a subnet mask? | `ask`: tutor_worker answers and cites page 3 |

Click **view trace** after a run. You should see agent, worker, tool and model events for that run.

## 5. Compare models

1. On **Compare models**, choose Computer Networks with task "Answer a question" and ask "What is TCP?". Both local models answer and show their latency.
2. Switch to "Grade an answer", pick a question, and enter a partial answer. The keyword and semantic graders give different scores.

## 6. Error handling

| Action | Expected |
|---|---|
| Upload a `.docx` or image file | "Unsupported file type…" |
| Upload a `.txt` renamed to `.pdf` | "File is not a valid PDF" |
| Submit an empty answer | "Write an answer first…" |
| Create a course with a 1-letter title | "Course title must be at least 2 characters." |
| Log in with a wrong password | "Invalid username or password" |
| Log out, then open `/courses/1` | Redirected to the login page |
