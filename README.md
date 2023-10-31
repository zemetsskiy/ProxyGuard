```
uvicorn main:app --reload
```

*Port problem solution*
```
lsof -i :8000
kill -9 <PID>
```