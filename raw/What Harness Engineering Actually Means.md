---
title: "What Harness Engineering Actually Means"
source: "https://www.youtube.com/watch?v=zYerCzIexCg"
author:
  - "[[What's AI by Louis-François Bouchard]]"
published: 2026-03-25
created: 2026-04-25
description: "► Learn more in our courses and social media: https://links.louisbouchard.ai/►My Newsletter (My AI updates and news clearly explained): https://louisbouchard..."
tags:
  - "clippings"
---
![](https://www.youtube.com/watch?v=zYerCzIexCg)

## Transcript

### Intro

**0:00** · If you've been hearing harness engineering everywhere lately and your first thought is, "Okay, so this is probably just prompt engineering with a nicer name." That's the first misconception to kill.

**0:13** · It's not. And it's not just a new term.

**0:16** · And the reason this matters is not just vocabulary, either. It tells you where AI is actually heading. By the end of this video, you should be able to tell the difference between prompt engineering, context engineering, and harness engineering. And more importantly, why the industry suddenly started caring about this now. What changed is pretty simple. Agents got good enough to be useful, but not reliable enough to trust on their own.

**0:46** · That's the entire story. Agents got good enough to be both useful and dangerous.

**0:52** · They now can do more than generating text or tokens. Useful enough that people started letting them write serious code, make real tool calls, and operate across long tasks. Dangerous enough that if you wrap them in nothing but a loop and a dream, they would confidently make the same stupid mistakes again and again.

**1:12** · Even I am guilty of letting Cloud Code or even Cloud Co-work loop for way too long sometimes before actually looking into what it's actually doing as I was doing something else in parallel like doing a set in the gym, which is totally not optimal to be working at the same time.

**1:33** · But still, we do that. We let agents work by themselves.

### Harness Engineering

**1:37** · And that's really where harness engineering came from. It came from pain. It came from people realizing that once the model is capable enough, the bottleneck stops being, "Can it generate \[clears throat\] code?" It becomes, "Can I make it behave reliably inside a real system I can control?"

**1:55** · The cleanest way to think about it is that prompt engineering is what to ask, context engineering is what to send the model so that it can answer confidently, and harness engineering is how the whole thing operates. Not just the tokens in the context, but the environment around the model or even around the agent.

**2:17** · The tools it can use, the permissions it has, the state it carries forward, the tests it has to pass, the logs you capture, the amount of retries, the checkpoints, the guardrails, the reviews, and evals that stop the system from drifting into nonsense. Context engineering lives inside that, and it still matters a lot, but it is not the whole story. A bigger context window does not magically turn a flaky agent into a reliable system.

**2:49** · The proof is that Opus 1 million context is actually hurting a lot of my work recently just because it costs way too much tokens. But anyways, that's not the goal of this video. The model is the engine. You can't do much without it.

**3:06** · But when you buy a car, it comes with it. You work on what you can bring value to. Context is part of that. The fuel, the oil change, and dashboard information. It's the things you can easily optimize and control. The harness is the rest of the car. The steering, the brakes, the lane boundaries, maintenance schedules, warning lights, and the fact that the doors shouldn't fall off on the highway.

**3:32** · If you only focus on the engine and fuel, you can still build a terrible car. You will drive, but it can be dangerous. This started becoming obvious around December 2025, and Karpathy was probably the first to talk about it with the inversion where his workflow went from mostly manual coding with a bit of agent help to mostly agent-driven coding with a bit of manual edits. That sounds like the story should be, "Oh, wow, the models won. We need to give them everything."

**4:02** · But that's not really the story. The story is that the moment agents got coherent enough to do a lot, everyone also discovered how brittle they were in real environments. This is why Cursor and Cloud Code are so popular. It's because it's not only the model. And speaking of brittle, well, models would claim a feature was done without actually running the test or even without really having implemented the feature.

### Longunning Agents

**4:31** · Cloud Co-work even did that to me this morning. They often lose the plot over long tasks. They would make local fixes that broke architectural boundaries.

**4:40** · They would get stuck in loops making tiny edits forever, which also stimulated a lot of research around compaction that I'd be happy to talk in an upcoming video if you'd like. Let me know. And so, Anthropic was one of the clearest early signals here. Their long-running agents post was basically a blueprint for a world where agents work in shifts across sessions without native memory between context windows.

**5:10** · So, instead of pretending the model will just remember everything, they externalized memory into artifacts, a structured feature list, a progress log, Git commits, an init script. They even split roles between an initializer agent and a coding agent. That's already harness thinking. You stop asking the model to be magically reliable and you start designing a system that makes reliability more plausible for the agent.

**5:40** · We started coding around LLMs and agents instead of around existing systems. Then, Mitchell Hashimoto gave the thing a name in early February 2026.

**5:53** · And honestly, I think this framing is why the term stuck. Every time the agent makes a mistake, don't just hope it does better next time. Engineer the environment so it can't make that specific mistake the same way again.

**6:10** · Improve the agents.md file based on actual bad behavior. Add scripts, linters, checks, and tools so the agent can verify and fix its own work. That's a very important mindset shift because it moves the burden away from waiting for the next model release and back to the builder, to us.

**6:30** · We stop saying the model is just dumb, I give up, and we start just building to improve models and adapt our tools and setup for it, which can even be done by non-coders with better skill files and prompting in general. Iterating with the agents to do better each time you use it.

**6:49** · For example, in each of my skills files in Cloud Code and in Cloud Co-work, I added a last step to reflect back on the whole interaction and the whole exchange and digest and understand what I liked, what I edited, what I didn't like, so that it can tweak its own skill to be better next time.

**7:11** · I also sometimes simply ask it to spend some time finding a better way to do a specific task. And if it works, I ask it to change the skill according to that.

**7:20** · It saved me tons and tons of tokens and time since I started doing this. And my skills file and just the processes in general got way better over time. Then, OpenAI made the whole thing impossible to ignore. Their recent report described building an internal product with roughly a million lines of code and zero manually written source code. Same for Cloud Code's creator who shared a tweet saying all past Cloud Code lines were pushed by Cloud Code itself. What matters there is not just the headline.

### Context Engineering

**7:52** · It's what they had to build around the agents to make that possible. Structured repo documentations as a real source of truth, agents.md files as maps, not a giant wall of text in a prompt. Layered architecture enforced by linters and tests. Agent-to-agent review loops before merging. Background cleanup agents fixing drifts. And that's not just writing prompts. That's infrastructure design around agents.

**8:22** · It's software engineering moving one level up. And this is where the link with context engineering becomes really useful because I think a lot of people are mixing these two terms up right now.

**8:34** · Context engineering is about making the task plausibly solvable for the model in a given moment. You give it the proper text to be able to answer. So, what information should be in the context window right now? What should be retrieved? What should be summarized?

**8:51** · What should be evicted? That's real work. And part of it can be automated by the agent itself. It's one of the main reasons many systems improved beyond dumb prompting. But a harness decides when the context gets loaded, which tools are available, which actions are allowed, how failures get handled, and what happens before anything gets called done.

**9:17** · Your harness is the infrastructure you build around the model. So, context engineering might make sure the model sees the right database schema, and harness engineering is the reason it still has to run the linter, pass the test, respect permissions, and save progress so it doesn't forget the objective three turns later.

**9:38** · One is what the model sees, the other is how the system behaves.

**9:43** · This also explains why people are talking about progressive disclosure so much. If you dump your entire company brain into one giant agents file, the agent doesn't become wiser. Usually, it just becomes worse. More noise, more context rot, more things silently ignored.

**10:04** · The better pattern seems to be a short map up front and deeper sources of truth pulled in only when needed. That's context engineering inside your harness.

**10:17** · The harness decides what surface and when, instead of treating the context window like a landfill.

**10:24** · Now, why does all of this matter beyond people building coding agents at all?

**10:29** · Because this is starting to look like the new way software gets built. Not fully, not cleanly, and definitely not safely by default, but the direction is becoming clearer. LangChain showed that by changing only the harness, not the model, they could move a coding agent from outside the top 30 to top five on the benchmark Terminal Bench 2.0. Same model, better system, better harness.

**10:57** · Stripe reportedly has agents producing over a thousand merged pull requests per week, but inside isolated environments with hard CI limits and escalation rules. DataDog pushed the ID further by treating production telemetry as part of the harness itself.

**11:17** · If performance regresses, that signal goes back into the loop, and that's not vibe coding. This is generate, validate, fix with observability to help. And there's an even more important implication here. The programmer's job is shifting, not disappearing, shifting.

**11:37** · Less time typing every line by hand, more time designing habitats where agents can do useful work without wrecking everything around them. More machine-readable documentation, more evals, more sandboxes, more permission boundaries, more structural tests, more logs, traces, and replayability.

**11:58** · Prompting is the easiest part here.

**12:01** · Reliability is the real work. And the honest version, though, is that none of this means agents are magically solved.

**12:10** · Memory still breaks, validation still misses things, tool use still creates security risk, harness depth is real because now your harness becomes its own product with its own bugs and drifts, and human attention becomes the real scarce resource. If agents can generate way more output than humans can carefully inspect, then rigor has to move into the system itself. Since we cannot review everything manually forever, we need checks we trust.

**12:42** · So, we need to build environments that fail safely, and we need traces that tell us why something went wrong.

**12:54** · So, when people ask where LLMs are heading, I think the better answer is that they are heading into systems, into workflows, agents, runtimes, and harnesses where more of the value comes from the orchestration, constraints, and feedback loops than from a prompt and a model that we share on social media.

**13:17** · The future is probably less one genius model does everything and more models operating inside well-engineered environments that make them usable. And that's why harness engineering matters.

**13:30** · It's not a trendy rename for prompting.

**13:32** · It's what shows up when you stop demoing intelligence and start trying to ship it. Thanks for watching throughout. I hope this video was useful, and if it was, please consider subscribing to see next week's video.