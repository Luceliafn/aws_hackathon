import streamlit as st
import boto3
import json
import logging
import uuid
logger = logging.getLogger(__name__)

REGION = 'us-west-2'

if "messages" not in st.session_state:
    st.session_state['messages'] = []

if 'agent_client' not in st.session_state:
    st.session_state['agent_client'] = boto3.client('bedrock-agent-runtime', region_name=REGION)

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid1())

# escolha fixa de agente e alias
st.session_state['agentId'] = 'OIA2DP7SBI'
st.session_state['aliasId'] = 'UFEVWBMLEC'


def gera_resposta_agente(input_text):

    enable_trace = False
    end_session = False

    # invoke the agent API
    agentResponse = st.session_state['agent_client'].invoke_agent(
        inputText=input_text,
        agentId=st.session_state['agentId'],
        agentAliasId=st.session_state['aliasId'], 
        sessionId=st.session_state['session_id'],
        enableTrace=enable_trace, 
        endSession= end_session,
    )
    event_stream = agentResponse['completion']
    try:
        for event in event_stream:        
            if 'chunk' in event:
                data = event['chunk']['bytes']
                partial_message = data.decode('utf8')
                yield partial_message
            elif 'trace' in event:
                logger.info(json.dumps(event['trace'], indent=2))
            else:
                raise Exception("unexpected event.", event)
    except Exception as e:
        raise Exception("unexpected event.", e)

if st.button('Começar nova sessão'):
    st.session_state['messages'] = []
    st.session_state['session_id'] = str(uuid.uuid1())


# escreve histórico de mensagens
# chat_container = st.container(height=700)
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace('$', '\$'))

# caixa de prompt
prompt = st.chat_input("Insira suas perguntas sobre um processo")

if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message = st.session_state['messages'][-1]['content']
        history = st.session_state['messages'][:-1]
        # stream = predict(message, history)
        stream = gera_resposta_agente(message)
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
