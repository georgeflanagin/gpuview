function gpuview
{
    if [ -z "$GPUVIEW_HOME" ]; then
        export GPUVIEW_HOME="$PWD"
    fi

    export OLDPYTHONPATH="$PYTHONPATH"
    export PYTHONPATH=/usr/local/hpclib
    command pushd "$GPUVIEW_HOME" >/dev/null
    python gpuview.py $@
    command popd >/dev/null
}

