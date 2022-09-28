# Environment setup

### Machine Configuration
* **OS:** Ubuntu 20.04
* **Kernel version:** 5.4.0-81-generic
* **Platform:** TGL-U
* **OpenVino version:** 2021.4.582

## 1. OpenVino installation
* Get the latest version of OpenVINO from:  [Click Here ](https://docs.openvinotoolkit.org/latest/openvino_docs_install_guides_installing_openvino_linux.html)
* Download the tar file by providing the details of the OS where you are going to install
* Untar the tar file
* Go to the directory l_openvino_toolkit_p_<OpenVINO_Version> 
* Run the following commands
```shell
  $ sudo -E ./install_openvino_dependencies.sh
  $ sudo -E ./install_GUI.sh
```
Leave everything to default and click on Next until last stage

Setup the environment: 
```shell
  $ source /opt/intel/<OpenVINO_Version>/bin/setupvars.sh
```