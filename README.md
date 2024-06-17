# [Chat Analyzer](https://chat-anlyzer.streamlit.app/)
Apply different analysis & data science tools on your Telegram / Whatsapp chat and get exciting insights!

An online version is available here - [Chat Analyzer](https://chat-anlyzer.streamlit.app/)

<img src="https://github.com/aloncohen1/chat-analyzer/assets/42881311/ca7d0912-792b-4519-bd6f-b2732b84a21b" width="500" height="300">


# How to run locally

First, you need to create a `secret.toml` by yourself. this file should be located at `~/.streamlit/secrets.toml` for macOS/Linux or `%userprofile%/.streamlit/secrets.toml` for Windows (Read more [here](https://docs.streamlit.io/develop/concepts/connections/secrets-management))

For this app, the `secret.toml` should contain the following values:

```
hf_api_token = "your_hf_code_here"
tracking_pass = "your_tacking_pass_here"
google_site_verification_code = "your_google_site_var_here"
```

The only relevant value your should update is the `hf_api_token`.<br>
See [here](https://huggingface.co/docs/hub/en/security-tokens) how to create your own token

Once your `secret.toml` is ready, run:
```
git clone https://github.com/aloncohen1/chat-analyzer.git
pip install -r /<local_path>/chat-analyzer/requirements.txt
streamlit run /content/chat-analyzer/Home.py
```
