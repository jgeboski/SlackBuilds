#!/bin/sh
export JAVA_HOME=@JAVA_HOME@
export PATH="${PATH}:${JAVA_HOME}/bin:${JAVA_HOME}/jre/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:@JAVA_LD@"
