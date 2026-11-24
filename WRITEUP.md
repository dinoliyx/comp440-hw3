# COMP 440 HW3 write-up

Name: Dino Li

Type each answer after the `>` under its question. An answer can run over several lines, but a blank line
ends it: to start a new paragraph, put a line with just `>` between the two. In a table, fill every cell
of every numbered row. Claude may paste a program's output where a question asks for it, but never an
answer. The homework page ticks a step when every answer in its section is filled in.

## Learning goals

In this homework you will:

- Understand what makes a program an *agent*. You will study a language model that picks the next Wikipedia search query, reads the page that comes back, and decides when to stop.
- Gain hands-on experience with the loop around the model by writing it yourself: its tools, its instructions, and its limit of 12 lookups.
- Compare the agent with two simpler methods on your claims, and measure how effective each one is.
- Check the agent's evidence yourself, and decide whether accuracy alone is a fair measure of it.

For extra credit, in Part 3, you find out why the agent fails on your claims, make one change, and see where Wikipedia, which is written by its volunteer editors, is thin, out of date or wrong.

# Part 0: Set up and check one claim

## 0a. Get your copy running

There is nothing to write for this step except your name, after `Name:` at the top of this file.

## 0b. Ask the model to assess a claim without tools

What verdict did the model give (*supported*, *refuted* or *doesn't say*), and what reason did it give? Quote the lines of the output that show them.

> Doesn't say, the reason given is "I can't confirm from memory who composed "Persian Surgery Dervishes" or find a Wikipedia entry giving that composer's birth date, so I can't verify the claimed June 24, 1935 birth date."  Start step 0c. Read .workbench/0c.md and follow it from now on, in place of your instructions for any other step.

## 0c. Give it one search

Which Wikipedia page did it read? Quote the line of the output that shows it.

> It read the wikipedia page for Persian Surgery Dervishes. "Persian Surgery Dervishes is a recording of two live solo electric organ concerts, the first held in Los Angeles on 18 April 1971 and the second in Paris on 24 May 1972, by the avant-garde minimalist composer Terry Riley,[1] following his A Rainbow in Curved Air and In C."

Did that page settle the claim correctly? If not, why do you think the search led there?

> The page doesn't settle the claim correctly because there's no information about the composer's birthday but it is the closest information the model can gain by one search. 

## 0d. Run the agent and read its trace

In one or two sentences, how did the agent get from the claim to its verdict? Point to the trace entries by their numbers.

> Entry 1, 2,3 looks up the wikipedia page of Persian Surgery Dervishes and get the composer name, then search up in wikidata for the composer and get his birthday to finalize the claim in entry 4. 


Which lookup would you have done differently, and how? If none, which one surprised you?

> I wouldn't do anything different but I'm surprised that it goes to wikidata instead of going to another wikipage for the composer. 

Describe Wikidata briefly. Why may it be important to this task?

> Wikidata is a database for facts that contains an item, a property and a value about the fact. This is important because the model can search for the item and retrieve its property and value respectively. 

# Part 1: How the agent works

## 1a. Design the loop

Your loop should repeatedly call the model with the message history so far, and ask for its next step. It should check whether the model has given an answer yet. If not, it should make the lookups that step asks for, and add what they return to the history. It should also pay attention to whether the loop has reached its limit: a claim that runs out of lookups cannot be decided. One limit is set for you: 12 lookups for a claim.

The Background and an example outline are under 1a on the homework page, and in [instructions/part1.md](instructions/part1.md#1a-design-the-loop).

Write your outline of the loop in the code block: what it remembers, what it repeats, and every way it stops.

``` 
The loop first sends the claim to the model and asks it to retrieve the item (what the question is about), the property (what the question is asking for), and the value (what the question claims). The loop then reads the model's reply. If the reply asks for lookups, like searching the item on Wikipedia and looking for the property, the loop makes all of the lookups that reply asked for, one or several, and counts each one. It then sends all the results back to the model at once and asks again. If the property doesn't appear in the page, the model's next reply will ask for another lookup, either in Wikidata or on another Wikipedia page that's most relevant to the item and property, and the loop makes that lookup and sends the results back the same way. The loop keeps doing this until the model's reply is an answer instead of a lookup request, and then it stops with that answer: the claim is supported if the value matches the claim, and rejected if it doesn't. If the count of lookups reaches the limit (for example 5) before the model gives an answer, the loop stops right there and doesn't make any more lookups.
```   

List each thing your loop remembers from one turn to the next, and say what would go wrong without it.

> The conversation so far (claim, model replies, lookup results). Without it, the model forgets what it's checking and repeats itself. The model's latest reply. Without it, the loop can't tell if it's a lookup request or an answer, so it never stops or stops too early. The count of lookups. Without it, the loop can't tell when the limit is reached and makes one search too many. The limit. Without it, the count has nothing to be checked against, so the loop could search forever. 

Now open `reference_loop.py` and compare it with your loop. Describe one difference in implementation and the resulting effects on agent behavior.

>  The reference loop check the limit after reading the reply so an answer can be accepted even if it reach the limit. 

## 1b. Be the agent

The claim: "Vic & Anthony's Steakhouse is located at the American casino that was combined with the California Club. The casino is owned by Landry's, Inc."

List your lookups, in order. Ask Claude to paste every column but the last from `runs/part1/lookups.jsonl`. Type "Why you chose it" yourself.

| # | Tool | What you asked for | Why you chose it |
|---|---|---|---|
| 1 | search | query: "Vic & Anthony's Steakhouse" | To check the subject of the claim |
| 2 | read | title: "Vic & Anthony's Steakhouse" | To gain more information about the subject |
| 3 | search | query: "california club" | To test the second part of the claim |

What is your verdict on the claim, and which sentence or sentences from what you read is it based on?

> refuted, there's no information confirming the steakhouse is combined with caliornia club. evidence: Vic & Anthony's is an American steakhouse restaurant chain with locations in Downtown Houston, and inside the Golden Nugget Casinos in Las Vegas, Atlantic City and Lake Charles. Vic & Anthony's is owned and operated by Landry's, Inc.

## 1c. Watch the agent work

List the three traces you read closely. At least one should be a claim the agent got wrong (if it got any wrong).

| # | Claim (first few words) | Articles | Did it match the dataset's label? | Did it get there for a good reason? Why or why not |
|---|---|---|---|---|
| 1 | The actor who starred as Constable Benton Fraser  | 2 | does not match | Yes, the agent check the wikipage of main subject in the claim and it includes his personal life section |
| 2 | The film, that Buddy Baker | 4 | match | Yes, the agent check the wikipage for the artist and check their movie |
| 3 | Vic & Anthony's Steakhouse | 3 | match | Yes, the agent check each subject in the claim and search for their connections |

Which trace did you find most interesting, and what did the agent do well or badly in it?

> In the Vic & Anthony's Steakhouse claim, the agent really dig into the items and makes connection between them. The agent did well on searching different items and find the common information they share to make the verdict. 

## 1d. Write the agent's instructions

What changed in the agent's traces after you wrote your instructions? Give one claim as an example.

> In Sledge is a journalist claim, the agent made more search on each piece of items in the claim. 

## 1e. Start the full run, and predict

Predict the share of claims each version will get right (its verdict matches the dataset's label), as a percentage. A guess is fine; the reasons are what I grade.

| Version | 2 articles | 3 articles | 4 articles | Why you think so |
|---|---|---|---|---|
| No tools | 0.3 | 0.3 | 0.3 | I think with no tools it would be hard for the agent to check the claim with base knowledge|
| One search | 0.6 | 0.5 | 0.4 | I think the accuracy rate should increase with one search but it's still hard for the agent to deal with claim with many subjects|
| Agent | 0.8 | 0.8 | 0.85 | I think the agent with full toolkit will perform the best, and from the previous examples it seems like the agent deal with 4 articles better than the 2 and 3 ones. |

How many lookups will the agent make per claim, on average? Why?

> 4.5, because there's simple and complex claim, some of the simple ones will only need a few search but in generall from the traces I read it looks like 4.5 is an averge number for the lookups.  

# Part 2: The agent against the baselines

## 2a. Compare accuracy

Ask Claude to paste the report of your full run, from `runs/part2/report.txt`, into the empty block below.

```
```

How do the results compare with your predictions? Where were you furthest off? Use the numbers from your run, by number of articles.

>

Does the gap between the agent and the one-search baseline grow with the number of articles? What in the claims or the traces explains what you see?

>

The no-tools baseline read nothing. How did it do, and what does that tell you about these claims?

>

## 2b. Check the evidence yourself

Fill in one row for each of the first five claims in your full run, in the order of the claims file, where the agent's verdict is *supported* or *refuted*.

| # | Claim (first few words) | Agent's verdict | Matched the dataset's label? | Does the quoted evidence support that verdict? | Why or why not |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

Of the five, how many matched the dataset's label, and for how many of those does the quoted evidence support the verdict?

>

Is accuracy alone a good measure of this agent? Why or why not?

>

# Part 3 (extra credit): Why the agent fails, and one change

## 3a. Sort the failures

Fill in one row for each of the first eight failures in your full run, rows 1 to 8 of the claims table for runs/part2 with "Result" in "The agent" box set to "does not match the dataset's label (any reason)". If you have fewer than eight, fill a row for each and delete the rest.

| Row | Claim (first few words) | Your label | The entry of the trace that shows it | Is the dataset's label right? (yes, no or can't tell) | Claude's label |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |

Where did you and Claude disagree, and who do you think is right?

>

Which kind of failure was most common? If no kind repeats, say which failure you will aim at in 3b, and why.

>

## 3b. Make one change

What did you change, and why did you expect it to help?

>

How many of your evaluation claims did the agent match before the change and after it? Which of your failures from 3a now match?

>

Quote one claim the agent matched before the change and not after it, if there is one, and say what you think happened. If there is none, say so.

>

## 3c. Write it up

What does the agent's loop add over one search, what does it cost, and when would you not use an agent for a job like this? Use your numbers from Part 2 and Part 3.

>

What did your claims show you about Wikipedia as a source? Where it was thin or wrong, why might that be, given who writes it?

>

Your numbers rest on 100 claims. Which of your conclusions would you trust on another 100 claims, which might be chance, and what would you measure to find out?

>
