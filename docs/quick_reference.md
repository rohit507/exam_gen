# Quick Reference

## Assignment Creation

  - How do I set up my development environment?
    - FIX LINK : (In the tutorial)[tutorial.html#setting-up-your-development-environment]

  - How do I set up a new assignment project?
    - FIX LINK : (In the tutorial)[tutorial.html#setting-up-the-project]

  - How do I add a classroom to a project?
    - FIX LINK : (In the tutorial)[tutorial.html#adding-a-classroom-and-roster-to-the-project]

  - How do I add a roster to a project?
    - FIX LINK : (In the tutorial)[tutorial.html#adding-a-classroom-and-roster-to-the-project]

  - How do I set the body text of a question?
    - Add link: minimal inline version in tutorial/writing_questions
    - minimal external file in `tut/proj_org`

  - How do I set the solution text for a question?
    - Add link: minimal inline version in tutorial/writing_questions
    - add link: More complex version in tut/adv_temp
    - minimal external file in `tut/proj_org`

  - What is the API for the rng provided to `user_setup`?
    - Add Link: python docs "Random.Random"

  - How do I format templates?
    - add Link: Jinja doccs lw1
    - add link: minimal notes in tut/cust_and_rand
    - add link: info on loops and whitespace in tut/adv_temp

  - What variables are available to the templates I use?
    - add link: minimal notes in tut/cust_and_rand

  - How do I pass new variables to my templates?
    - add link: minimal notes via user_setup in tut/cust_and_rand

  - How do I add packages or modify the LaTeX header?

  - LaTeX is giving me an error, how can I figure out where it's coming from?

  - How do I nest questions or add sub-questions?
    - add link `tut/multi-part`

  - How do I share information between questions and sub-questions? or an
    exam and its questions?
    - add line `tut/multipart`

  - Can I organize questions and sub-questions in sub-directories of the
    main assignment?
    - yes, see `tut/proj_org`

  - Can I split questions and sub-question into multiple files?
      - yes, see `tut/proj_org`

  - How do I use external files in my assignment?
    - see `tut/ext_assets`


## Build Process

  - How do I build an exam for a single student?
    - add link: somewhere in tutorial for minimal version

  - How can I change the settings for a single student?

  - How do I build exams in bulk?
    - add link: somewhere in tutorial for minimal version

  - How do I build solution keys?
    - add link: somewhere in tutorial for minimal version

## Build Debugging

  - How can I test roster parsing?
    - FIX LINK : (Testing via `list`)[tutorial.html#available-build-actions]
    - FIX LINK : (Testing via `parse-roster`)[tutorial.html#testing-roster-parsing]

  - How can I see what information is associated with a student?
    - FIX LINK : (Testing via `parse-roster`)[tutorial.html#testing-roster-parsing]

  - How can I add new template variables?

  - What do the various logging and debug files in `~data` mean?
    - add link: For template rendering see tut/cust_and_rand

## Development Tasks

  - How do I create a new roster parser?
    - ADD LINK : should eventually be in
      `dev_guide/adding_components/roster_parsers.md`

## Useful External Links

  - Python's Raw String Format

  - Jinja2 Template Format Documentation

  - Jinja2 and LaTeX quirks:
    - spaces to separate latex braces `{ {` so we can use jinja braces `{{`
    - be careful about escape codes, you usually don't want

## Example Index
