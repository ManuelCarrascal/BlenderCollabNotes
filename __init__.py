bl_info = {
    "name": "BlenderCollabNotes",
    "blender": (3, 60, 0),
    "category": "Interface",
}

import bpy


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
            ("All", "All", "All categories")
        ],
        name="Category",
        default="All"
    )


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
            row.label(text=f"Object: {note.object_reference}")

            row = box.row()
            row.label(text="Category:")
            split = row.split(align=True)
            split.label(text=note.category, icon='BLANK1')
            split.prop(note, "category", text="", emboss=False)

            row = box.row()
            row.label(text=f"Title: {note.note_title}")
            row = box.row()
            row.label(text=f"Description: {note.note_description}")

            row = box.row()
            if note.is_edit_mode:
                row.operator("object.edit_object_note", text="Update").note_index = i
            else:
                row.operator("object.edit_object_note", text="Edit Note").note_index = i
            row.operator("object.remove_object_note", text="Delete Note").note_index = i


class AddObjectNotePanel(bpy.types.Panel):
    bl_label = "Create Notes"
    bl_idname = "PT_AddObjectNotePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        is_edit_mode = scene.object_notes_temp.is_edit_mode

        row = layout.row()
        row.label(text="Note Title:")
        row = layout.row()
        row.prop(scene.object_notes_temp, "note_title", text="")

        row = layout.row()
        row.label(text="Note Description:")
        row = layout.row()
        row.prop(scene.object_notes_temp, "note_description", text="")

        row = layout.row()
        row.label(text="Category:")
        row = layout.row()
        row.prop(scene.object_notes_temp, "category", text="")

        row = layout.row()
        if not scene.object_notes_temp.note_title or not scene.object_notes_temp.note_description:
            row.enabled = False
        if is_edit_mode:
            row.operator("object.edit_object_note", text="Update").note_index = scene.object_notes_temp.note_index
        else:
            row.operator("object.add_object_note", text="Add Note")


class AddObjectNoteOperator(bpy.types.Operator):
    bl_idname = "object.add_object_note"
    bl_label = "Add Note to Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        selected_obj = context.active_object

        if selected_obj:
            note = scene.object_notes.add()
            note.object_reference = selected_obj.name
            note.note_title = scene.object_notes_temp.note_title
            note.note_description = scene.object_notes_temp.note_description
            note.category = scene.object_notes_temp.category

        scene.object_notes_temp.note_title = ""
        scene.object_notes_temp.note_description = ""

        return {'FINISHED'}


class EditObjectNoteOperator(bpy.types.Operator):
    bl_idname = "object.edit_object_note"
    bl_label = "Edit Object Note"
    bl_options = {'REGISTER', 'UNDO'}

    note_index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        note = scene.object_notes[self.note_index]

        if (note.note_title != scene.object_notes_temp.note_title or
                note.note_description != scene.object_notes_temp.note_description):
            note.note_title = scene.object_notes_temp.note_title
            note.note_description = scene.object_notes_temp.note_description
        else:
            self.report({'INFO'}, "No changes were made to the note.")

        note.is_edit_mode = not note.is_edit_mode

        scene.object_notes_temp.note_title = ""
        scene.object_notes_temp.note_description = ""

        return {'FINISHED'}


class RemoveObjectNoteOperator(bpy.types.Operator):
    bl_idname = "object.remove_object_note"
    bl_label = "Delete Object Note"
    bl_options = {'REGISTER', 'UNDO'}

    note_index: bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        scene.object_notes.remove(self.note_index)

        return {'FINISHED'}


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


def unregister():
    bpy.utils.unregister_class(ObjectNoteProperty)
    bpy.utils.unregister_class(ObjectNotesPanel)
    bpy.utils.unregister_class(AddObjectNoteOperator)
    bpy.utils.unregister_class(EditObjectNoteOperator)
    bpy.utils.unregister_class(RemoveObjectNoteOperator)
    bpy.utils.unregister_class(AddObjectNotePanel)

    del bpy.types.Scene.object_notes
    del bpy.types.Scene.object_notes_temp
    del bpy.types.Scene.object_notes_category_filter


if __name__ == "__main__":
    register()