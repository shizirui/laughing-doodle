package yiqi_compare;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class text1 {
    public static void main(String[] args) {
        // 创建一个ScheduledExecutorService实例，指定一个线程
        ScheduledExecutorService executor = Executors.newSingleThreadScheduledExecutor();

        // 定义一个Runnable任务
        Runnable task = new Runnable() {
            @Override
            public void run() {
                try {
                    // Python脚本的路径
                    String pythonScriptPath = "H:/ecilipse/程序/shizirui/src/check.py";
                    String templatePath = "img/main.png"; // 替换为模板图像的路径
                    
                    // 构建命令
                    List<String> command = new ArrayList<>();
                    command.add("python"); // 或者是 "python3"，具体取决于你的Python安装
                    command.add(pythonScriptPath);
                    command.add(templatePath);
                    
                    // 创建进程构建器
                    ProcessBuilder processBuilder = new ProcessBuilder(command);
                    
                    // 启动进程
                    Process process = processBuilder.start();
                    
                    // 读取进程输出
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println(line);
                    }
                    
                    // 读取进程错误流
                    BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
                    while ((line = errorReader.readLine()) != null) {
                        System.err.println(line);
                    }
                    
                    // 等待进程结束
                    int exitCode = process.waitFor();
                    System.out.println("Exited with code: " + exitCode);
                    
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        };

        // 每隔2000毫秒（2秒）执行一次任务
        executor.scheduleAtFixedRate(task, 0, 1, TimeUnit.MILLISECONDS);
    }
}
