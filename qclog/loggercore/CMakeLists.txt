cmake_minimum_required(VERSION 3.16)

qt_add_qml_module(loggercore
    URI qclog.loggercore
    VERSION 1.0
    SOURCES
        loggercore.h loggercore.cpp
    RESOURCES
        schema.sql
)

target_link_libraries(loggercore PRIVATE Qt6::Sql)
target_link_libraries(loggercoreplugin PRIVATE Qt6::Sql)
