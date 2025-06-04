SCRIPT_PATH="ACTS_frontend.py"

echo "Trying to run with python3..."
if python3 "$SCRIPT_PATH"; then
    echo "Script ran successfully with python3."
else
    echo "python3 failed, trying with python..."
    if python "$SCRIPT_PATH"; then
        echo "Script ran successfully with python."
    else
        echo "Script failed with both python3 and python."
        exit 1
    fi
fi
