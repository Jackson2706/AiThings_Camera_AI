I.Tổng quan 
=====================

AiThings_Camera_AI là một phần của hệ thống phát hiện vi phạm và phạt nguội . Hệ thống sẽ giúp tăng cường giám sát, từ đó tăng hiệu quả quản lý giao thông vốn phức tạp ở Việt Nam 

Hiện nay đã có ứng dụng của camera phạt nguội tuy nhiên gặp phải nhiều hạn chế do các camera chỉ gửi dữ liệu video về máy chủ để xử lí làm cho lượng xử lí tại máy chủ là quá lớn, Tốn nhiều nhân lực để duy trì , vận hành cũng như rủi do quá tải tại trung tâm kiểm soát. Do đó Camera_AI sẽ giải quyết được nhược điểm trên do phần xử lí sẽ được thực hiện ngay tại camera. 

### Các chức năng tích hợp trong dự án: 
 - Phát hiện đối tượng vi phạm luật giao thông 

- Phát hiện loại lỗi vi phạm của phương tiện ô tô, xe máy, xe bus 

- phát hiện biển số xe của đối tượng vi phạm 

Sau khi phát hiện sự kiện lỗi, đẩy dữ liệu đối tượng lên hệ thống để lưu trữ và xử lí 

### Dữ liệu vi phạm bao gồm: 
- Loại phương tiện 

- Lỗi vi phạm 

- Thời gian vi phạm 

- Ảnh vi phạm 

- Video vi phạm 

- Ảnh biển số xe 

- Biển số xe 


II.Cài đặt và chạy dự án trên jetson AGX 
=============
1.Tải code về jetson AGX:
======

    $ git clone https://github.com/Jackson2706/AiThings_Camera_AI.git
	

2.Cài đặt thư viện 
=============
#### PyTorch v1.7.0 (JetPack 4.4) 

	$ wget https://nvidia.box.com/shared/static/wa34qwrwtk9njtyarwt5nvo6imenfy26.whl -o torch-1.7.0-cp36-cp36m-linux_aarch64.whl 
	$ sudo apt-get install python3-pip libopenblas-base libopenmpi-dev  
	$ pip3 install Cython 
	$ pip3 install numpy torch-1.7.0-cp36-cp36m-linux_aarch64.whl 

#### Torchvision v0.5.0 (compatible with PyTorch v1.4.0) 
	$ sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev 
	$ git clone --branch v0.8.1 https://github.com/pytorch/vision torchvision  
	$ cd torchvision 
	$ export BUILD_VERSION=0.8.1  # where 0.x.0 is the torchvision version   
	$ sudo python3 setup.py install 
	$ cd ../  
	$ pip install 'pillow<7' 

#### Opencv 
OpenCV v4.1.1 (Python2.7/3.6+ JetPack4.3/4.4) 

	$ cd ~ 
	# purge old-version 
	$ sudo apt-get purge libopencv* 
	$ bash <(wget -qO- https://github.com/yqlbu/jetson-packages-family/raw/master/OpenCV/install_opencv4.1.1_jetson.sh) 

#### Pandas 

Pandas v1.2.0(Latest) 

	$ pip3 install -U pandas –user 

#### Seaborn 
Seaborn v0.11.1(Latest) 

	$ pip3 install -U seaborn --user 

#### Numpy 

Numpy v1.19.4(Latest) 

	$ pip3 install -U numpy --user 

 #### Pycuda 

Pycuda v2019.1.2(Latest) 

	$ pip3 install -U pycuda –user 

#### Scipy 
Scipy v1.6.0(Latest) 

	$ apt-get install libatlas-base-dev gfortran 
	$ pip3 install -U scipy –user 

 

#### onether library 

Một số thư viện khác phù hợp với Jetpack version  

	link: https://gitee.com/Cheng_Loon/jetson-packages-family-good#jetson-packages-family 
Chạy chương trình 
=====
 Sau khi hoàn tất các thư viện, có thê chạy toàn bộ dự án bằng lệnh sau: 

 	$ ./run.sh 