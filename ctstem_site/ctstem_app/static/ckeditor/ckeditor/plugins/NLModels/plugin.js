/**
 * NetLogo Web Models Library Plugin
 * @license Copyright (c) 2020, CT-STEM. All rights reserved.
 * @author Connor Bain
 */

/**
 * @fileOverview Plugin for browsing NetLogo Web Models Library.
 * This relatively simple plugin allows one to browse the NetLogo Web Models
 * Library without leaving the CT-STEM site. It consists of a simple dialog
 * popup that presents the user with a drop-down of all compatible NetLogo Web
 * Models Library models. These models are actually directly fetched from the
 * NetLogo Web site meaning they are always kept perfectly up to date.
 *
 * A user can select one of the models and the dialog will automatically preview
 * and resize the NetLogo Web model. If the user then wants to insert this model,
 * they need only click the "Insert Model" button. The plugin will then insert
 * an iframe element, src-ed to the offical NetLogo Web models library hosted on
 * netlogoweb.org, and insert said iframe element at the user's cursor within
 * their CKEditor instance. Additionally, it will set the width and height of the
 * frame to fully display the model.
 *
 * The plugin requires both the ajax and 'iframedialog' plugins be installed in
 * your CKEditor instance.
 *
 * WARNING: Note, because this inserts iframes linked directly to netlogoweb.org
 * this means that any models created via this method ARE SUBJECT TO MODIFICATION
 * and will AUTOMATICALLY be updated to their latest versions. These changes
 * can be tracked at github.com/NetLogo/models.
 */

// Register the plugin within the editor.
CKEDITOR.plugins.add( 'NLModels', {
	requires: [ 'ajax', 'iframedialog' ],

	// Register the icon
	icons: 'NLModels',

	// The plugin initialization logic goes inside this method.
	init: function( editor ) {

		// Add the command to CKEditor
    editor.addCommand( 'addNLModel', new CKEDITOR.dialogCommand( 'NLModelsDialog' ) );

		// Create the toolbar button that executes the above command.
		editor.ui.addButton( 'NLModels', {
			label: 'Insert NetLogo Web Model',
			command: 'addNLModel',
		});

		// Specify the dialog format and function
		CKEDITOR.dialog.add( 'NLModelsDialog', this.path + 'dialogs/NLModels.js' );
	}
});
