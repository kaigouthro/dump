from textwrap import dedent

import streamlit as st

# Create a Streamlit interface for editing the attributes of the class
st.title("Complex Prompts Editor")

class MyNewClass:
    def __init__(
        self, name, system, template, input_variables, output_variables, meta_requests, selections
    ):
        self.name = name
        self.system = system
        self.template = template
        self.input_variables = input_variables
        self.output_variables = output_variables
        self.meta_requests = meta_requests
        self.selections = selections

    def __repr__(self):
        return str(self)

    def __str__(self):
        return dedent(
            "{"
            + f"""
            "name"            : {self.name},
            "system"          : {self.system},
            "template"        : {self.template},
            "input_variables" : {self.input_variables},
            "output_variables": {self.output_variables},
            "meta_requests"   : {self.meta_requests},
            "selections"      : {self.selections}
        """
            + "}"
        )



def create_key_value_pair_interface(key, keynames):
    """
    Creates a streamlit interface that can add/remove keynames to a list,
    each keyname in the list, create one text input
    to associate with that key, creating a dict of key/val pairs from the input
    """

    st.subheader(f":blue[{key.split(':')[-1]}]")
    menu_keys = list(keynames.keys())
    menu_keys.append("new")
    # Add a button to remove a keyname from the list
    selectkey = st.selectbox("Select Keyname to Remove", menu_keys, 0, key=f"{key}_selectkey")

    keyname = (
        st.text_input("Enter Keyname", key=f"{key}.keyname")
        if selectkey in {"new", None}
        else selectkey
    )

    # Add a button to add a keyname to the list
    if st.button("Add Keyname", key=f"{key}_add_keyname"):
        keynames[keyname] = ""

    if st.button("Remove Keyname", key=f"{key}_remove_keyname"):
        if selectkey:
            keynames.pop(selectkey)

    # Create a dictionary of key/val pairs
    return {
        keyname: st.text_input(
            f"Enter Value for Keyname {keyname}", value, key=f"{key}.{keyname}"
        )
        for (keyname, value) in keynames.items()
    }


def create_list_editor(key, items):
    """Creates a streamlit interface that can add/remove items to a list, and for each item in the list, create one text input to edit the item, creating a list of strings from the input"""
    st.subheader(f":orange[{key.split(':')[-1]}]")
    menu_keys = list(items)
    menu_keys.append("new")
    new_items = set(items)
    if "new" in new_items:
        items.remove("new")

    items.copy()
    # Add a button to remove an item from the list
    select_item = st.selectbox("Select Item", menu_keys, key=f"{key}_selectitem")

    item = (
        st.text_input("Enter Item", key=f"{key}.item")
        if select_item in {"new", None}
        else select_item
    )
    # Add a button to add an item to the list
    if st.button("Add Item", key=f"{key}_add_item"):
        new_items.add(item)
        return list(new_items)

    if st.button("Remove Item", key=f"{key}_remove_item"):
        if item:
            new_items.remove(item)
            return list(new_items)

    # Return the list of strings

    return list(new_items)


def edit_class(myprompt):
    st.text_input("Name", myprompt.name)
    st.text_input("System", myprompt.system)
    st.text_input("Template", myprompt.template)

    columns = st.columns(2)
    keynum = 0
    with columns[0]:
        with st.container(border=True):
            input_variables = create_list_editor(
                f"{keynum}:Input Variables", myprompt.input_variables
            )
            keynum += 1
    with columns[1]:
        with st.container(border=True):
            output_variables = create_key_value_pair_interface(
                "Out Variables", myprompt.output_variables
            )
            keynum += 1
    with columns[0]:
        with st.container(border=True):
            meta_keys = create_list_editor(
                f"{keynum}:Meta Requests", list(myprompt.meta_requests.keys())
            )
            keynum += 1
            for key in meta_keys:
                if key not in myprompt.meta_requests:
                    myprompt.meta_requests[key] = {}
                myprompt.meta_requests[key] = create_key_value_pair_interface(
                    f"{keynum}:{key}", myprompt.meta_requests[key]
                )
                keynum += 1
    with columns[1]:
        with st.container(border=True):
            select_keys = create_list_editor(
                f"{keynum}:Selectors", list(myprompt.selections.keys())
            )
            keynum += 1
            for key in select_keys:
                if key not in myprompt.selections:
                    myprompt.selections[key] = {}
                myprompt.selections[key] = create_key_value_pair_interface(
                    f"{key}{keynum}", myprompt.selections[key]
                )
                keynum += 1

        # Print the updated attributes of the class
    return myprompt


def new_prompt():
    return MyNewClass(
        name="My New Class",
        system="My System",
        template="My Template",
        input_variables=[],
        output_variables={},
        meta_requests={},
        selections={},
    )


st.session_state.created_prompts = st.session_state.get("created_prompts", {})
PROMPTMENU = list(st.session_state.created_prompts.keys())
PROMPTMENU.extend(["new"])

SELECT_PROMPT = st.selectbox("Select Prompt", PROMPTMENU, key="select_prompt")

if SELECT_PROMPT in {None, "new"}:
    select_prompt = st.text_input("Input New Name", "new", key="prompt_name")
    if st.button("Create New Prompt"):
        if SELECT_PROMPT not in st.session_state.created_prompts:
            st.session_state.created_prompts[SELECT_PROMPT] = new_prompt()
        st.rerun()
else:
    st.session_state.created_prompts[SELECT_PROMPT] = edit_class(
        st.session_state.created_prompts[SELECT_PROMPT]
    )
    if st.button("Save Changes"):  # if st.session_state.created_prompts[select_prompt]:
        st.rerun()

for p in st.session_state.created_prompts.values():
    st.markdown(p)
