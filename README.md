# I tried building a small package manager for python, with custom python Linter


We all have used package managers like npm, pip, etc. These tools help us to add dependencies into a project with configuration, without a programmer having 
to install them locally on system making the project build process easy. I have even used a custom Linting for python source files in the project to prevent bad code practices and 
prevent usage of certain mallicious functions. While building the source files you will get a warning depending on the issue, but you can also disable warnings. Linting helps 
to analyze source code in form of abstract syntax tree which can help to prevent bad code or bugs.

<h1>here are some tests so far: </h1>

<p>initialization</p>
<img src="/montages/init_pm.png" height="210" />

<p>Warning for local imports inside functions</p>
<img src="/montages/local-import-warning.png" height="210"/>

<p>discouraging usage of the Eval function</p>
<img src="/montages/preventing-injection-attacks!.png" height="210" />

<p>preventing warnings</p>
<img src="/montages/by-pass-warning.png" height="210" />
