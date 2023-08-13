mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"seth@major7apps.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[theme]\n\
base=\"light\"\n\
\n\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml