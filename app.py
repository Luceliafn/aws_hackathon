import streamlit as st
import boto3
import json
import logging
import uuid
logger = logging.getLogger(__name__)

REGION = 'us-west-2'



if "messages" not in st.session_state:
    st.session_state['messages'] = []

if 'num_processo' not in st.session_state:
    st.session_state['num_processo'] = None

if 'agent_client' not in st.session_state:
    st.session_state['agent_client'] = boto3.client('bedrock-agent-runtime', region_name=REGION)

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid1())

if 'agents' not in st.session_state or True:
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)

    agents = {
        agent['agentName']: {
            'agentId': agent['agentId'], 
            'agentAliases': dict()
        } for agent in bedrock_agent.list_agents()['agentSummaries']
    }
    for name, info in agents.items():
        for alias in bedrock_agent.list_agent_aliases(agentId=info['agentId'])['agentAliasSummaries']:
            info['agentAliases'][alias['agentAliasName']] = alias['agentAliasId']


    st.session_state['agents'] = agents

# escolha fixa de agente e alias
st.session_state['agentId'] = 'OIA2DP7SBI'
st.session_state['aliasId'] = 'UFEVWBMLEC'


def gera_resposta_agente(input_text):

    session_state = {
        'knowledgeBaseConfigurations': [
            {
                'knowledgeBaseId': "L4MSFKO2YY",
                'retrievalConfiguration': {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 20,
                        "overrideSearchType": "HYBRID",
                        "filter": {
                            "equals": {
                                "key": "num_processo",
                                "value": str(st.session_state['num_processo'])
                            }
                        }
                    }
                }
            }
        ]
    }

    enable_trace:bool = False
    end_session:bool = False

    # invoke the agent API
    agentResponse = st.session_state['agent_client'].invoke_agent(
        inputText=input_text,
        agentId=st.session_state['agentId'],
        agentAliasId=st.session_state['aliasId'], 
        sessionId=st.session_state['session_id'],
        enableTrace=enable_trace, 
        endSession= end_session,
        sessionState= session_state
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


# Seletores de agente e alias
# col_agent, col_alias = st.columns(2)
# agent = col_agent.selectbox('Agent', st.session_state['agents'].keys())
# alias = col_alias.selectbox('Alias', st.session_state['agents'][agent]['agentAliases'].keys())

# guarda escolha
# st.session_state['agentId'] = st.session_state['agents'][agent]['agentId']
# st.session_state['aliasId'] = st.session_state['agents'][agent]['agentAliases'][alias]

col_num_processo, col_botao_atualizar = st.columns(2)

num_processo = col_num_processo.text_input(label='Número do processo')
if col_botao_atualizar.button('Atualizar processo'):
    st.session_state['num_processo'] = num_processo
    st.session_state['messages'] = []

# escreve histórico de mensagens
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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

# 07001777820248070011
# liste os envolvidos
# quem é a autora?
# 07097029720238070018
# liste os envolvidos no processo 07001777820248070011
# liste os envolvidos no processo 07097029720238070018
# liste os envolvidos no processo 07430185520238070001

# liste os envolvidos no processo 07206392320238070001
# liste os envolvidos no processo 07251462720238070001
# liste os envolvidos no processo 07471652720238070001
# liste os envolvidos no processo 10023333420178260123
# liste os envolvidos no processo 10075424420208260554
# faça um resumo do processo 07251462720238070001
# faça um resumo do processo 07206392320238070001
# faça um resumo do processo 07471652720238070001
# faça um resumo do processo 10023333420178260123
# faça um resumo do processo 10075424420208260554





# script - vídeo


# Faça um resumo da sentença do processo 07471652720238070001
# Qual o valor do débito gerado pela autora neste processo?


# Qual o valor do débito gerado pela autora no processo 07471652720238070001?
