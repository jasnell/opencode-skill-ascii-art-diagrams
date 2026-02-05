# An opencode skill for correctly drawing ascii art diagrams

Agents are still remarkably bad at creating ascii art diagrams, frequently
getting alignment wrong, semantics of the various diagrams incorrect, etc.
This skill is designed to make the process more rigorous.

You'll notice that the skill text appears to rather overdo emphasize the
mandated steps... this is because many models review the skill, see text
like "You MUST do..." then decide that the step is optional and completely
skip it, resulting in misaligned and incorrect diagrams.

Sigh.

I already raised teenagers tho, so I'm used to it. Repetition is good.
Opus 3.6 appears to do a pretty good job with the mandated instructions
tho, so at least there's hope.

That said, the workflow can add significant time to the generation of the
diagrams, emphasizing correctness over speed (which is the point). So if
you need just a quick "it's ok to be a little wrong" diagram, explicitly
state that in your prompt and the skill should skip the more detailed steps.
