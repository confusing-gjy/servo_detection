cmake_minimum_required(VERSION 3.22)

# 1. 必须在 project() 之前强制设置架构，防止 cpsid i 报错
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_TRY_COMPILE_TARGET_TYPE "STATIC_LIBRARY")

# 强制注入架构参数到全局编译器变量
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mcpu=cortex-m3 -mthumb -mfloat-abi=soft")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -mcpu=cortex-m3 -mthumb")
# 增加 -T 参数指定链接脚本文件
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -mcpu=cortex-m3 -mthumb --specs=nosys.specs -T \"${CMAKE_SOURCE_DIR}/STM32F103XX_FLASH.ld\" -Wl,--gc-sections")

# 2. 项目名称（必须与报错信息中的 target 名一致）
set(CMAKE_PROJECT_NAME servo_detection)
project(${CMAKE_PROJECT_NAME} C ASM)

# 3. 基础编译器设置
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)

# 4. 【关键点】先创建一个空的可执行目标，让子目录能找到它
add_executable(${CMAKE_PROJECT_NAME})

# 5. 引入 CubeMX 生成的子目录（它会往这个 servo_detection 目标里填代码）
add_subdirectory(cmake/stm32cubemx)

# 强制指定输出文件名带有 .elf 后缀
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES OUTPUT_NAME "${CMAKE_PROJECT_NAME}.elf")

# 自动生成 HEX 的命令（修改了输入文件名）
add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
        COMMAND D:/ST/STM32CubeCLT_1.20.0/GNU-tools-for-STM32/bin/arm-none-eabi-objcopy.exe -O ihex ${CMAKE_PROJECT_NAME}.elf ${CMAKE_PROJECT_NAME}.hex
        COMMENT "Generating HEX file..."
)