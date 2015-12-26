# leetcode-best-answers

A pdf document with three top voted answers in the discussion forum for each problem on leetcode.com.

## How it was made

Nothing fancy here... Basically:

- get discussion url for each question based on its url pattern
- crawl (python, lxml) top three voted answers for each question given a discussion url
- write answers for each question into mongodb
- style and display the answers locally via node.js/express.js
- generate pdf with wkhtmltopdf

Note there are answers for locked questions in this pdf. The reason is that while the problem is locked, the dicussion for the problem isn't.


## Note

All answers in the document are attributed to their authors. If you see your answers in there and would rather your answer not be included, send me a note at gnijuohz@gmail.com.


## Me

- [twitter](https://twitter.com/gnijuohz)
- 欢迎用我的app [GeeksforGeeks Reader](https://itunes.apple.com/us/app/geeksforgeeks-reader-read/id991254978?mt=8).

## Feedback

Just open an issue.
