(TeX-add-style-hook
 "exam_standalone.jn2"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "12pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("adjustbox" "export")))
   (add-to-list 'LaTeX-verbatim-environments-local "lstlisting")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "lstinline")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperref")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "lstinline")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art12"
    "lastpage"
    "ifthen"
    "hyperref"
    "tikz"
    "times"
    "graphicx"
    "wrapfig"
    "amsmath"
    "amsfonts"
    "enumitem"
    "xspace"
    "listings"
    "epsfig"
    "epstopdf"
    "gensymb"
    "color"
    "adjustbox"
    "textcomp")
   (TeX-add-symbols
    '("comment" 1)
    '("homework" 2)
    '("set" 1)
    '("port" 1)
    '("stateName" 1)
    '("ignore" 1)
    '("answer" 1)
    '("code" 1)
    '("nextprob" 0)
    '("notsolution" 1)
    '("solution" 1)
    "ie"
    "eg"
    "eventually"
    "finally"
    "globally"
    "nextstate"
    "until"
    "QuadSpace"
    "HalfSpace"
    "FullSpace"
    "EndProof"
    "answer")
   (LaTeX-add-environments
    "compactItemize"
    "theorem"
    "lemma"
    "corollary"
    "definition"
    "fact"
    "assumption"
    "proof"
    "proofsketch"
    "notation"
    "intuition"
    "note"
    "convention"
    "example"
    "question"
    "remark"
    "observation"
    "proposition")
   (LaTeX-add-counters
    "probcount")
   (LaTeX-add-color-definecolors
    "darkblue"))
 :latex)

