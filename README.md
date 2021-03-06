# Traffic Sign Recognition
This project is developed for the exam of Computer Vision at Alma Mater Studiorum of Bologna (UNIBO).

The aim of this project is to create an image classificator capable of reconizing traffic signs. 

The dataset comes from the famous German traffic sign benchmark [[link](http://benchmark.ini.rub.de/)] that provides more than 50 000 images relative to 43 different classes.

The project main task is to classify the traffic sign images which come from the dataset. These images contain only the ROI (Region of Interest) and some pixel as contour. To achieve this target I will use a Convolution Neural Network (CNN).

## 1) Classification application
This python application can be executed in two different ways: 
1. **interactive mode** (-m 0): the application will start with an interactive menu, which can be used to execute an action and, after that action, ask for the next one.
2. **script mode** (-m 1 -a [actions]): the application will execute a sequence of actions and, at the end, will stop the execution

### Possible actions
| **CODE** | **DESCRIPTION**                        |
|:--------:|----------------------------------------|
|     0    | Download training and testing datasets |
|     1    | Prepare training datatable csv file    |
|     2    | Split training data                    |
|     3    | Prepare test data                      |
|     4    | Train all images                       |
|     5    | Load existing model from json          |
|     6    | Test model performance                 |


default value is `-m 0`

To see the full list of possible arguments type `-h` or `--help`


### Installation

To install this application follow these steps:

- step 1 - clone

```
git clone https://github.com/ale8193/traffic-sign-recognition.git
cd traffic-sign-recognition
```
- step 2 - download dependences
```
pip install --no-cache-dir -r requirements.txt
```
- step 3 - init project structure
```
python main.py -m 1 -a 0,1,2,3
```
- step 4 (optional) - build dockers images and create containers
```
docker build -t traffic-sign-recognition .
docker build -t jupyter ./docker/jupyter/ 
docker build -t tensorboard ./docker/tensorboard/
```

### Execution

##### Interactive mode
```
python main.py
```
Then simply choose the action from the menu

##### Script mode
```
python main.py -m 1 -a [actions separated by comma] [other args]
```

##### Docker execution
- run the main application and then use `docker logs cnn-app` to see the output or remove `-d` flag:
```
docker run -d -v $(pwd)/data:/usr/src/app/data -v $(pwd)/log:/usr/src/app/log -v $(pwd)/model:/usr/src/app/model --name cnn-app traffic-sign-recognition python main.py <args>
```
- run tensorboard and then navigate to `http://localhost:6006`:
```
docker run -d -v $(pwd)/log:/tensorboard -p 6006:6006 --name tensorboard tensorboard tensorboard --logdir=/tensorboard/<log_folder>
```
- run jupyter and then use `docker logs jupyter` to copy your token and finally navigate to `http://localhost:8888` :
```
docker run -d -v $(pwd)/:/jupyter -p 8888:8888 -e JUPYTER_FILE_PATH='iteractive_analysis.ipynb' --name jupyter jupyter
```
