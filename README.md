# webhooks-testing

Trying out GitHub webhooks. Steps to reproduce are at https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks .

To run it:
1. Do `ngrok http 4567` at the command line
1. Note the url it gives you use that as payload to create a webhook in GitHub  
    - Url will change on every run, so webhook needs to be updated in every session
1. Use `application/json` as content type
1. Generate some random characters with e.g. `hexdump -n 16 -e '4/4 "%08X" 1 "\n"' /dev/urandom`
1. Set that as the secret in the webhook and export it as `SECRET_TOKEN` in your shell
1. Install dependencies with `pipenv install`
1. Run with `pipenv run python server.py`
1. Do stuff in GitHub (push, create issues, comment etc) and watch it scroll over the screen in your terminal  
    - Easy way to generate events is to re-deliver old deliveries
