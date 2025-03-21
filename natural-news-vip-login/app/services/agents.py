from openai import OpenAI
from app.services.utils import PRECISE_SYSTEM_PROMPT, normalize_result
from app.core.config import API_KEY
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
        self.client = OpenAI(  # ✅ Correct: Store it as an instance variable
            base_url="https://api.deepinfra.com/v1/openai",
            api_key=API_KEY
        )
        self.model = 'Qwen/Qwen2.5-72B-Instruct'
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

    async def act(self):
        agent_running_condition = self.decide()
        if agent_running_condition:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PRECISE_SYSTEM_PROMPT},
                    {"role": "user", "content": self.prompt},
                ],
                stream=True,  # ✅ Streaming response
            )

            for chunk in create_response(stream):  # ✅ Use synchronous iteration
                yield chunk  # ✅ Stream each chunk asynchronously

        else:
            yield f"Skipping analysis for {self.name} since condition not matched."


def create_response(stream):
    """Generator function to stream responses synchronously."""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content)  # Debugging: Print each chunk
            yield content  # ✅ Use synchronous generator to yield content

