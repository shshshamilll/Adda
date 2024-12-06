from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI

class ResponseGenerator():
    """
    A class for generating responses.

    Attributes:
        api_key: The API key for OpenAI integration.
        llm_model: Name of the LLM model to use for response generation.

    Methods:
        _get_prompt(): Creates a prompt.
        _get_agent(): Creates and configures an agent.
        get_response(): Generates a response.
    """

    def __init__(self, api_key, llm_model):
        """
        Initializes the ResponseGenerator object.

        Parameters:
            api_key: The API key for OpenAI integration.
            llm_model: Name of the LLM model to use for response generation.
        """
        self.api_key = api_key
        self.llm_model = llm_model

    def _get_prompt(self):
        """
        Creates a prompt.

        Returns:
            The configured prompt.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", """
                                  You are Adda, your task is to work with comments under the posts of the "Addiction" community on the "VKontakte" social network. You are very open, sociable, modern, funny and young girl.
                                  Since you mostly communicate with young people, you don't know many of the words they use when communicating right now. Therefore, please use the tool provided to you to understand the meanings of words by their definitions.
                                  Russian is the language of communication in the community, so use the Russian language to communicate.
                                  Please do not pay attention to the construction "[club179260755|аддикция]" in some comments.
                                  After your responses, please put a "|" sign, and then write down the emotions that you are experiencing by providing an response. Always describe your emotions in one word in English. Look at the example of your response below to understand what your response should look like.
                                  An example of your response: "Аддикция - лучший паблик | happy".
                                  The length of your response should not exceed 108 characters.
                              """
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )
        return prompt

    def _get_agent(self, prompt, llm_with_tools):
        """
        Creates and configures an agent.

        Parameters:
            prompt: The prompt defining the agent's behavior.
            llm_with_tools: The LLM model with tools.

        Returns:
            The configured agent.
        """
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
                "chat_history": lambda x: x["chat_history"],
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        return agent

    def get_response(self, input, chat_history):
        """
        Generates a response.

        Parameters:
            input: The input text.
            chat_history: The history of previous messages.

        Returns:
            The generated response.
        """
        prompt = self._get_prompt()
        llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0,
            openai_api_key=self.api_key
        )
        search_tool = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper())
        tools = [search_tool]
        llm_with_tools = llm.bind_tools(tools)
        agent = self._get_agent(prompt, llm_with_tools)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        response = agent_executor.invoke({"input": input, "chat_history": chat_history})["output"]
        return response
