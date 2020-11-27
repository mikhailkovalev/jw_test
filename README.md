### API examples
 - `your-host:8000/posts`
```json
{
    "count": <Total count of posts in DB>,
    "next": "link/to/next/page",
    "previous": "link/to/previous/page",
    "results": [
        {
            "publisher": {},
            "url": "link/to/post/detail"
        },
        ...
    ]
}
```
 - `your-host:8000/posts/<post_pk>`
```json
{
    "publisher": {
        "username": "admin"
    },
    "url": "http://localhost:8000/posts/1/",
    "attachments": [
        {
            "title": "Video Content Title",
            "position": 1.0,
            "views_count": <Views Count>,
            "files": [
                {
                    "file": "/link/to/videofile"
                }
            ],
            "subtitles": [
                {
                    "file": "/link/to/subtitles/file"
                }
            ],
            "resourcetype": "VideoContent"
        },
        {
            "title": "Audio Content Title",
            "position": 2.0,
            "views_count": 56,
            "files": [
                {
                    "file": "/link/to/audiofile",
                    "bitrate": <Audio File Bitrate>
                }
            ],
            "resourcetype": "AudioContent"
        },
        {
            "title": "Text Content Title",
            "position": 3.0,
            "views_count": 56,
            "content": "Text",
            "resourcetype": "TextContent"
        }
    ]
}
```