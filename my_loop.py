"""Your agent's loop, which you design in step 1a. The homework page says what the
loop is for, under "1a. Design the loop" (also in instructions/part1.md), and the
check tells you each rule it must follow when your loop breaks it.

You design the loop as an outline in plain words, in WRITEUP.md under 1a. The
loop below the line that says where it goes is Claude's translation of that
outline, written with the parts in loop_parts.py: each line of your outline is a
comment, with about one line of Python for it under it. To change the loop,
change your outline and ask Claude to translate it again.

Check it after each translation. The check uses a scripted stand-in for the
model and for Wikipedia, so it needs no key and costs nothing:

    uv run python check_loop.py

Part 0 runs the agent on the reference loop. Once every rule passes, the agent
runs on this loop and no other: the runs of 1c and later need it to pass.
"""

import anthropic

# The names below include every one the file had before the parts, so that a loop written
# then still runs.
from agent import (ACCEPTED, DECLINED, INSTRUCTIONS, MAX_REJECTED, MAX_STEPS, MODEL, NO_ANSWER,
                   OUT_OF_STEPS, RAN_OUT, REJECTED, REJECTED_TOO_OFTEN, REMINDED, REMINDER,
                   TOOLS, answer_problem, clean_answer, finish, run_tool)
from loop_parts import Conversation


def run_agent(claim, client=None, max_steps=MAX_STEPS, lookup=run_tool):
    """Check one claim. Returns what talk.accept() or talk.stop() returns."""
    client = client or anthropic.Anthropic()
    system = INSTRUCTIONS.read_text()
    messages = [{"role": "user", "content": f"Claim: {claim}"}]
    trace, read_so_far = [], []
    talk = Conversation(claim, client, system, messages, trace, read_so_far, lookup)
    steps = 0          # lookups made so far
    rejected = 0       # answers sent back so far

    # Your loop should repeatedly call the model with the message history so far, and ask for
    # its next step. It should check whether the model has given an answer yet. If not, it should
    # make the lookups that step asks for, and add what they return to the history. It should
    # also pay attention to whether the loop has reached its limit: a claim that runs out of
    # lookups cannot be decided.
    # ---- your loop goes below this line (step 1a) ----

    # The loop first sends the claim to the model and asks it to retrieve the item (what the
    # question is about), the property (what the question is asking for), and the value (what the
    # question claims).
    reply = talk.ask()

    # (The repeat: "The loop keeps doing this until ...", below. Python puts the repeat here, at
    # the top of what it repeats.)
    while True:

        # The loop then reads the model's reply.
        # (no new Python: the reply is already in hand)

        # If the reply asks for lookups, like searching the item on Wikipedia and looking for the
        # property, the loop makes all of the lookups that reply asked for, one or several, and
        # counts each one.
        if reply.lookups:
            made = []
            for call in reply.lookups:
                made.append((call, talk.run(call)))
                steps += 1

            # It then sends all the results back to the model at once and asks again.
            for call, result in made:
                talk.give(call, result)
            talk.send_results()
            reply = talk.ask()

        # If the property doesn't appear in the page, the model's next reply will ask for another
        # lookup, either in Wikidata or on another Wikipedia page that's most relevant to the item
        # and property, and the loop makes that lookup and sends the results back the same way.
        # (no new Python: this is the next time round the repeat)

        # The loop keeps doing this until the model's reply is an answer instead of a lookup
        # request, and then it stops with that answer: the claim is supported if the value matches
        # the claim, and rejected if it doesn't.
        if reply.answer is not None:
            return talk.accept(reply.answer, steps)

        # If the count of lookups reaches the limit (for example 5) before the model gives an
        # answer, the loop stops right there and doesn't make any more lookups.
        if steps >= max_steps:
            return talk.stop(RAN_OUT, steps)
