import promptlayer
import json

 # Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)


promptlayer.api_key = data["PROMPTLAYER_API_KEY"]
openai = promptlayer.openai


def get_prompt(prompt_id):
    template_dict = promptlayer.prompts.get(prompt_id)
    template = template_dict['template']
    return template

def update_persona_prompt_template(persona_name, persona):
    try:
        prompt_template = promptlayer.prompts.get(
            persona_name
        )
        prompt_template['template'] = persona
        promptlayer.prompts.publish(
            prompt_name=persona_name, 
            prompt_template=prompt_template
        )
        return True
    except Exception as e:
        print(e)
        return False