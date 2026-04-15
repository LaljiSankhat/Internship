# from fastapi import FastAPI

# app = FastApi()


# @app.get("/")
# def hello_world():
#     return {"message": "Hello, World!"}
# leetcode 2069 walking robot simulation 2

def solve(commands: List[str], obstacles: List[List[int]]) -> int:
    x = 0
    y = 0
    direction = 0
    for command in commands:
        if command == "G":
            if direction == 0:
                y += 1
            elif direction == 1:
                x += 1
            elif direction == 2:
                y -= 1
            elif direction == 3:
                x -= 1
        elif command == "L":
            direction = (direction + 1) % 4
        elif command == "R":
            direction = (direction - 1) % 4
        if (x, y) in obstacles:
            return (x, y)
    return (x, y)

def solve(pid: List[int], ppid: List[int], kill: int) -> List[int]:
    pass