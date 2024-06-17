from streamlit_agraph import Config

def Gui(directed: bool):
    return Config(width='100%',
                height=700,
                directed=directed,
                physics=False,
                nodeHighlightBehavior=False, 
                highlightColor="#F7A7A6", # or "blue"
                collapsible=False,
                node={'labelProperty':'label'},
                )

