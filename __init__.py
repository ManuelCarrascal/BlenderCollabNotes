# Blender addon information
bl_info = {
    "name": "BlenderCollabNotes",
    "blender": (3, 60, 0),
    "category": "Interface",
}

import bpy

# Function to update object references when the scene is updated
def update_object_references(dummy):
    scene = bpy.context.scene
    for note in scene.object_notes:
        if note.object_reference in bpy.data.objects:
            # Update the object reference to the object's current name
            note.object_reference = bpy.data.objects[note.object_reference].name

# Register the update function as a dependency graph update post-handler
bpy.app.handlers.depsgraph_update_post.append(update_object_references)

# Custom property group for storing object notes
class ObjectNoteProperty(bpy.types.PropertyGroup):
    object_reference: bpy.props.StringProperty(
        description="Referenced Object Name"
    )
    note_title: bpy.props.StringProperty(name="Note Title")
    note_description: bpy.props.StringProperty(name="Note Description")
    is_edit_mode: bpy.props.BoolProperty(default=False)
    category: bpy.props.EnumProperty(
        items=[
            ("High", "High", "Category of high importance"),
            ("Medium", "Medium", "Medium importance category"),
            ("Low", "Low", "Category of low importance"),
            ("No Category", "No Category", "Note without category"),
        ],
        name="Category",
        default="No Category"
    )

# Custom panel for displaying and editing object notes
class ObjectNotesPanel(bpy.types.Panel):
    bl_label = "Objects Notes"
    bl_idname = "PT_ObjectNotesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.label(text="Filter by Category:")
        row.prop(scene, "object_notes_category_filter", text="")

        object_notes = scene.object_notes

        for i, note in enumerate(object_notes):
            if scene.object_notes_category_filter != "All" and note.category != scene.object_notes_category_filter:
                continue

            if i > 0:
                layout.separator()

            box = layout.box()
            row = box.row()

            # Display object reference or search field if in edit mode
            if note.is_edit_mode:
                row.prop_search(note, "object_reference", bpy.data, "objects", text="Object")
            else:
                row.label(text=f"Object: {note.object_reference}")

            row = box.row()

            # Display title or editable title field if in edit mode
            if note.is_edit_mode:
                row.prop(note, "note_title", text="Title")
            else:
                row.label(text=f"Title: {note.note_title}")

            row = box.row()

            # Display description or editable description field if in edit mode
            if note.is_edit_mode:
                row.prop(note, "note_description", text="Description")
            else:
                row.label(text=f"Description: {note.note_description}")

            row = box.row()

            # Display category or editable category field if in edit mode
            if note.is_edit_mode:
                row.prop(note, "category", text="Category", emboss=False)
            else:
                row.label(text=f"Category: {note.category}")

            row = box.row()

            # Display buttons for editing or deleting notes
            if note.is_edit_mode:
                row.operator("object.edit_object_note", text="Finish Edit").note_index = i
            else:
                row.operator("object.edit_object_note", text="Edit Note").note_index = i
                row.operator("object.remove_object_note", text="Delete Note").note_index = i

# Custom panel for creating new object notes
class AddObjectNotePanel(bpy.types.Panel):
    bl_label = "Create Notes"
    bl_idname = "PT_AddObjectNotePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.label(text="Note Title:")
        row = layout.row()
        row.prop(scene.object_notes_temp, "note_title", text="")

        row = layout.row()
        row.label(text="Note Description:")
        row = layout.row()
        row.prop(scene.object_notes_temp, "note_description", text="")

        row = layout.row()

        # Display search field for object reference
        row.prop_search(scene.object_notes_temp, "object_reference", bpy.data, "objects", text="Object")

        row = layout.row()
        row.label(text="Category:")

        # Display category field if not in edit mode
        if not scene.object_notes_temp.is_edit_mode:
            row.prop(scene.object_notes_temp, "category", text="")

        row = layout.row()
        # Disable the add note button if title or description is empty
        if not scene.object_notes_temp.note_title or not scene.object_notes_temp.note_description:
            row.enabled = False
        row.operator("object.add_object_note", text="Add Note")

# Custom operator for adding a new object note
class AddObjectNoteOperator(bpy.types.Operator):
    bl_idname = "object.add_object_note"
    bl_label = "Add Note to Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        selected_obj = context.active_object

        if selected_obj:
            # Create a new note with the selected object's information
            note = scene.object_notes.add()
            note.object_reference = selected_obj.name
            note.note_title = scene.object_notes_temp.note_title
            note.note_description = scene.object_notes_temp.note_description
            note.category = scene.object_notes_temp.category

        # Reset temporary note data
        scene.object_notes_temp.note_title = ""
        scene.object_notes_temp.note_description = ""

        return {'FINISHED'}

# Custom operator for editing an object note
class EditObjectNoteOperator(bpy.types.Operator):
    bl_idname = "object.edit_object_note"
    bl_label = "Edit Object Note"
    bl_options = {'REGISTER', 'UNDO'}

    note_index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        note = scene.object_notes[self.note_index]

        # Toggle edit mode
        note.is_edit_mode = not note.is_edit_mode

        return {'FINISHED'}

# Custom operator for removing an object note
class RemoveObjectNoteOperator(bpy.types.Operator):
    bl_idname = "object.remove_object_note"
    bl_label = "Delete Object Note"
    bl_options = {'REGISTER', 'UNDO'}

    note_index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        # Remove the selected object note
        scene.object_notes.remove(self.note_index)

        return {'FINISHED'}

# Register the classes and properties
def register():
    bpy.utils.register_class(ObjectNoteProperty)
    bpy.utils.register_class(ObjectNotesPanel)
    bpy.utils.register_class(AddObjectNoteOperator)
    bpy.utils.register_class(EditObjectNoteOperator)
    bpy.utils.register_class(RemoveObjectNoteOperator)
    bpy.utils.register_class(AddObjectNotePanel)

    bpy.types.Scene.object_notes = bpy.props.CollectionProperty(type=ObjectNoteProperty)
    bpy.types.Scene.object_notes_temp = bpy.props.PointerProperty(type=ObjectNoteProperty)
    bpy.types.Scene.object_notes_category_filter = bpy.props.EnumProperty(
        items=[
            ("High", "High", "Category of high importance"),
            ("Medium", "Medium", "Medium importance category"),
            ("Low", "Low", "Category of low importance"),
            ("No Category", "No Category", "Note without category"),
            ("All", "All", "All categories")
        ],
        name="Category",
        default="All"
    )

# Unregister the classes and properties
def unregister():
    bpy.utils.unregister_class(ObjectNoteProperty)
    bpy.utils.unregister_class(ObjectNotesPanel)
    bpy.utils.unregister_class(AddObjectNoteOperator)
    bpy.utils.unregister_class(EditObjectNoteOperator)
    bpy.utils.unregister_class(RemoveObjectNoteOperator)
    bpy.utils.unregister_class(AddObjectNotePanel)

    # Remove custom properties
    del bpy.types.Scene.object_notes
    del bpy.types.Scene.object_notes_temp
    del bpy.types.Scene.object_notes_category_filter

# Run the registration function if the script is executed directly
if __name__ == "__main__":
    register()
