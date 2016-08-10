# Leetcode Best Answers

## How

Selenium driver is used to fetch the urls of top voted answers for each question. `urls.txt` is generated. `answers.py` parses this file and write answers into a MongoDB. You can use `urls.txt` to do your own thing. Its format is:

```
question_num:number_of_answer_count_follows_this_line
answer_url
answer_url
...
```

`number_of_answer_count_follows_this_line` is usually `10`


## Improvement

Selenium driver is used to get `urls.txt` because the discussion forum does not order the answers by votes by default. To do that you need to log in and choose that option.  
Since the `requests`

## Note

All answers in the document are attributed to their authors. If you see your answers in there and would rather your answer not be included, send me a note at gnijuohz@gmail.com.

Also be responsible if you use this script to crawl leetcode. Use `time.sleep`.

## App

There is an app too! [Leetcoder](https://itunes.apple.com/us/app/leetcoder/id1069760709?mt=8).

Check out [GeeksforGeeks Reader](https://itunes.apple.com/us/app/geeksforgeeks-reader-read/id991254978?mt=8) as well!

## Feedback

Just open an issue.
