# JHAuto 
## 项目结构
```
--JHAuto
   |
   --config         配置文件
   |
   --logger         日志
   |
   --logs           生成的日志文件
   |
   --pages          页面类
   |
   --report         生成的测试报告
   |
   --running        启动目录
   |
   --screenshots    UI失败用例截图
   |
   --testcases      测试用例
   |
   --testdata       测试数据
   |
   --tools          driver等工具
   |
   --UIElements     Web页面元素
   |
   --utils          公用方法
   |
   --requirements.txt
```

## 运行
cd到当前项目running文件夹下，执行以下命令，将执行config/config.py配置的UI_TestCase_DIR下所有测试文件
```python
python test_runner.py
```
可以通过参数-c指定运行测试文件夹
```python
python test_runner.py -c 'BIAPI'
```
日志文件和测试报告将分别在logs和report目录生成







   