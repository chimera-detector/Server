# CHIMERA Stance Detector

![CHIMERA_ICON](https://image.flaticon.com/icons/png/128/571/571122.png)

## Overview

### CHIMERA Stance Detector  have following objectives
* Easy to recognize the **Fake News and Clickbaits**  in real world.
* Support strong prediction engine to recognize whether the article is Fake News or not.
* Let people know that we have to protect ourselves from the fake information from the internet such as Fake News.
* (In the business wise) Let company know how their website that has many of featured article headlines is clean or not by the hazard of Fake News or Clickbaits.

### CHIMERA Stance Detector Components
CHIMERA Stance Detector exists as major 2 different part, which means the one is server that  can process the request from the user interface directly using embedded ***Artificial Neural Network*** the other one is the user interface as i mentioned right before that supposed to launched as ***Browser Extension*** program such as chrome extension. The user interface will help people to recognize Fake News or Clickbaits more easily than the detection engine itself.
And we have subComponents below those two major component. A explanation of those will be attached soon.

### Specifications & Installation
As I mentioned previous section, CHIMERA Stance Detector has been built upon the existing artificial neural network model. So, we have to force to use same environmental specification where the neural network could work. here is the specification

> Python === 2.7.*
> Tensorflow === 0.12.1

I've tested python 2.7.5 is working well, but it is not working on python 3. we working on  to migrate from python2 to python3 but the massive code changes are required, so now we recommend to follow environmental specifiaction. also, tensorflow version 0.12.1 has not being distributed for window OS user, it has been distributed only for mac and linux user since that version of tensorflow is the version before the release officially.
Except the python specification, I made file called `requirements.txt` that has required python module to run the CHIMERA Stance Detector. So, after download python 2.7 successfully, then type below commands onto command line.Below commands only works for mac and linux now. will update window OS guideline soon.

```sh
$ git clone [this_project]
$ cd [this_project]
$ pip install virtualenv       
$ source venv/bin/activate       
$ pip install -r requirements.txt
```

## How to use?
1. Running the server locally. we assume that we already running the server with using virtual environment as we said in previous section (note that you are in the root folder of this project)

    ```sh
    $ python src/merged_server.py
    ```

2. Check the functionality via launched Website when we running the server `https://127.0.0.1:3000` or `https://localhost:3000`

3. You may have certificate errors to access Website that running on localhost server, then you can make certificates on this project, use below command to create new certificates and do step 1, 2 again and if they works well then jump into step 4.

    ```sh
    $ openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    ```

4. Now you can use the Website to check easily the functionality. but you can simply check by sending the url request itself since our communication between [browser extension] and the server will use HTTP protocol. feel free to explore!! I will attach the simple HTTP request for little help.

    > `https://localhost:3000/detect/headline="my name is seounghanSong"`
    > `https://localhost:3000/predict/URL="https://edition.cnn.com/~"`

### Referenced Project & Related Works

we referenced many related & previous works for this problem to build customer service using those suggested techniques. we proudly suggest what we referenced for this project

* [Cisco - SWEN IN THE SOLAT] : https://blog.talosintelligence.com/2017/06/talos-fake-news-challenge.html
* [Athene Systems] : https://arxiv.org/pdf/1806.05180.pdf
* [University of London Machine Reading Group] : https://arxiv.org/pdf/1707.03264.pdf

[this_project]: <https://github.com/chimera-detector/experienceWindow>
[browser extension]: <https://github.com/chimera-detector/experienceExtension>
[Cisco - SWEN IN THE SOLAT]: <https://github.com/Cisco-Talos/fnc-1>
[Athene Systems]: <https://github.com/hanselowski/athene_system>
[University of London Machine Reading Group]: <https://github.com/uclmr/fakenewschallenge>
