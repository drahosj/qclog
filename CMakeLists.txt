cmake_minimum_required(VERSION 3.16)

project(qclog VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Qt6 REQUIRED COMPONENTS Qml Sql)

qt_standard_project_setup()

qt_policy(SET QTP0001 NEW)

add_subdirectory(qclog/loggercore)

