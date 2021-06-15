# Setup develope environment

Create conda environmnt
```shell
conda create -n battlesnake python=3.8.3
```

Activate conda environment
```shell
conda activate battlesnake
```

Install dependency using pip
```shell
python -m pip install -r requirements.txt
```

When you are finish, deactivate conda environment
```shell
conda deactivate
```

# Running Your Battlesnake Locally

Eventually you might want to run your Battlesnake server locally for faster testing and debugging. You can do this by installing [Python 3.8](https://www.python.org/downloads/) and running:

```shell
python server.py
```

**Note:** You cannot create games on [play.battlesnake.com](https://play.battlesnake.com) using a locally running Battlesnake unless you install and use a port forwarding tool like [ngrok](https://ngrok.com/).


Testing your api with curl
```shell
curl -X POST -H "Content-Type: application/json" -d @test-data.json http://0.0.0.0:8080/start
```

Switch learning mode in runtime
```shell
curl -X GET -H "Accept: application/json" -H "Content-Type: application/json" -d @test-data.json http://0.0.0.0:8080/switch
```
