from openai import OpenAI

from vip_login.utils import PRECISE_SYSTEM_PROMPT, normalize_result
incompleted_messages = []


class Agent:
    def __init__(self, name):
        self.name = name

    def perceive(self, input_data):
        """Receive input from the environment."""
        raise NotImplementedError("Perceive method must be implemented.")

    def decide(self):
        """Make decisions based on perceived input."""
        raise NotImplementedError("Decide method must be implemented.")

    def act(self):
        """Perform an action based on the decision."""
        raise NotImplementedError("Act method must be implemented.")


class InputAgent(Agent):
    def perceive(self, input_data):
        self.topic = input_data

    def decide(self):
        return f"Proceeding with research on: {self.topic}"

    def act(self):
        print(self.decide())
        return self.topic


class AnalyzingAgent(Agent):
    def __init__(self, name, prompt, running_condition=""):
        super().__init__(name)
        self.prompt = prompt
        self.client = OpenAI(
            base_url="http://35.170.240.5:8081",
            api_key="aRMEhvlClTxqYosKSPrJ7BXCQQLrPy1Rf5e6SY2JMWgKgO1P0QaVUbOMCWvdWcDo"
        )
        self.model = 'LLaMA_CPP'
        self.running_condition = running_condition

    def perceive(self, topic):
        self.topic = topic

    def decide(self):
        if self.running_condition != "":
            result = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"Just answer one word yes or no. {self.running_condition}"}],
            )
            return normalize_result(result.choices[0].message.content) == "yes"
        else:
            return True

    def act(self):
        agent_running_condition = self.decide()
        if agent_running_condition:
            full_response = ""
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PRECISE_SYSTEM_PROMPT},
                    {"role": "user",
                     "content": f"{self.prompt}"}],
                stream=False,
            )
            full_response, total_tokens = create_response(stream)
            return full_response, total_tokens
        else:
            return f"Skipping analysis for {self.name} since condition not matched."


def create_response(stream):
    # full_response = ""
    # # Handle streaming response
    # for chunk in stream:
    #     if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
    #         full_response += chunk.choices[0].delta.content
    #     # incompleted_messages[-1]["content"] = full_response
    # return full_response
    choices = stream.choices
    if choices:
        response = choices[0].message.content
    else:
        response = 'No content available'
    total_tokens = stream.usage.total_tokens
    return response, total_tokens
