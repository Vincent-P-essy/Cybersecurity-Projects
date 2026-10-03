cmake_minimum_required(VERSION 3.31)
project(network-traffic-analyzer)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Boost REQUIRED COMPONENTS program_options)
add_executable(network-traffic-analyzer main.cpp
        "include/capture/pcapCapture.hpp"
        src/capture/pcapCapture.cpp
        "include/cli/argsParse.hpp"
        include/packet/packet.hpp
        include/packet/IP.hpp
        src/packet/IP.cpp
        include/stats/protocolStats.hpp
        src/stats/protocolStats.cpp
        src/packet/packet.cpp
        src/cli/argsParse.cpp
        include/cli/filter.hpp
        src/cli/filter.cpp
        include/TUI/view.hpp
        src/TUI/view.cpp
)

include(FetchContent)

set(FETCHCONTENT_UPDATES_DISCONNECTED ON)
set(FETCHCONTENT_QUIET OFF)

FetchContent_Declare(ftxui
        GIT_REPOSITORY https://github.com/arthursonzogni/ftxui.git
        GIT_TAG        v5.0.0
        GIT_PROGRESS   TRUE
        GIT_SHALLOW    TRUE
        EXCLUDE_FROM_ALL
)
FetchContent_MakeAvailable(ftxui)


target_link_libraries(network-traffic-analyzer
        pcap
        Boost::program_options
        ftxui::screen
        ftxui::dom
        ftxui::component
)

include(CTest)
if(BUILD_TESTING AND CMAKE_SYSTEM_NAME STREQUAL "Linux")
    add_library(pcap_unavailable MODULE tests/pcap_unavailable.c)
    foreach(help_flag --help -h)
        add_test(NAME help_without_interfaces_${help_flag}
            COMMAND ${CMAKE_COMMAND} -E env
                "LD_PRELOAD=$<TARGET_FILE:pcap_unavailable>"
                $<TARGET_FILE:network-traffic-analyzer> ${help_flag})
        set_tests_properties(help_without_interfaces_${help_flag}
            PROPERTIES PASS_REGULAR_EXPRESSION "Network Traffic Analyzer")
    endforeach()
endif()
