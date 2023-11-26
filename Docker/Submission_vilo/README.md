# Overview

You will have to download the zipped image from this link: https://drive.google.com/drive/folders/1sutmuCkkW2ms6mq4w-K6D-06s89wJ_FP?usp=sharing 

This file has been modified by team TeslaV100 

There are three main files in this submission 

1. The docker image file (submission_vilo.tar.gz) and a python script (_main.py_), which expose a service **/test** on a fixed port (7502) within the container. 
2. The _deploy.sh bash script, when run with sudo, will run the container and expose its fixed port (7502) to the hose machine's port.
3. The _test.sh_ bash script recive `host`, `port` and `filename`, and communicate with the script in the container using the exposed port to retrieve the needed text.


## Testing Guide
You can test out this sample on an UNIX system with `docker` and `curl` installed and `sudo` privilege. Perform the following command from inside the folder as work directory:
- Load the docker image with `docker load < submission_vilo.tar.gz`. This one needs sudo
- Run the docker image with `bash deploy.sh`. This one needs sudo
- Test the docker with the `test.vi` file using `bash test.sh localhost 7502 test.vi`. By default this command output the result to stdout, and you can redirect it to a file by appending `> file_of_your_choosing.txt`
- You can test with any text file that you want by using `bash test.sh localhost 7502 <Your text file name>`


