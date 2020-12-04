/**
 * NetLogo Web Models Library Plugin
 * @license Copyright (c) 2020, CT-STEM. All rights reserved.
 * @author Connor Bain
 */

/**
 * @WARNING, if the naming / organization method at the below ever changes, these
 * functions would need to be modified, as would the CONSTANTS above.
 * @reference https://github.com/NetLogo/Galapagos/blob/master/app/assets/javascripts/models.coffee
 *
 * These are current as of 12/3/2020 -- CPB
 *
 * Example URL for iframe src:
 * https://netlogoweb.org/web?https://netlogoweb.org/assets/modelslib/Curricular%20Models/Connected%20Chemistry/Connected%20Chemistry%20Gas%20Combustion.nlogo
 */
var NETLOGOWEB_SITE = "https://netlogoweb.org"
var MODEL_JSON_PATH = "/model/list.json"
var MODEL_STATUSES_JSON_PATH = "/model/statuses.json"
var NLW_QUERY_SELECTOR = "/web?"
var NLW_MODEL_ASSET_PATH = "/assets/"

var NLW_MODEL_PATH_FULL = "public/modelslib/"
var NLW_MODEL_PATH_PARTIAL = "public/"

// Define the dialog
CKEDITOR.dialog.add( 'NLModelsDialog', function( editor ) {
  return {
    title: 'NetLogo Models Library',
    minWidth: 600,
    minHeight: 200,
    // Manually override button appearance
    buttons: [
      CKEDITOR.dialog.cancelButton.override( {} ),
      CKEDITOR.dialog.okButton.override( { label : 'Insert Model'} ),
    ],
    // Dialog window content definition.
    contents: [
      {
        // Definition of the tab (page).
        id: 'tab',
        label: 'NetLogo Models Library',
        // The tab content.
        elements: [
          {
            // Select element to pick the model to preview
            type: 'select',
            id: 'model-picker',
            label: 'Select an option from the dropdown below to preview the model and then click Insert Model',
            items: [ ],
            // Called by the main setupContent method call on dialog initialization.
            setup: function( element ) {
              // Add a default option
              this.add('-- select a model to preview -- ', '')
            },
            onChange: function() {
              // Set the iframe src to the selected option
              this.getDialog().getContentElement('tab', 'nlw-preview').getElement().setAttribute('src',this.getValue())
            },
          },
          {
            // iframe element we use to load the model into
            type: 'iframe',
            id: 'nlw-preview',
            src: ''
          }
        ]
      }
    ],

    onLoad: function() {

      var dialog = this
      // Fetch the NLW Models Library resources we need
      var modelJSON = CKEDITOR.ajax.load( NETLOGOWEB_SITE + MODEL_JSON_PATH, function( modelJSON ) {
        var modelNames = JSON.parse(modelJSON)
        var statusesJSON = CKEDITOR.ajax.load( NETLOGOWEB_SITE + MODEL_STATUSES_JSON_PATH, function( statusesJSON ) {
          var modelStatuses = JSON.parse(statusesJSON);
          // Go through the models and get rid of any that don't compile on NLW
          for ( model of modelNames ) {
            if (modelStatuses[model].status != "not_compiling")
              dialog.getContentElement('tab', 'model-picker').add(
                model.substring(NLW_MODEL_PATH_FULL.length, model.length),
                NETLOGOWEB_SITE + NLW_QUERY_SELECTOR + NETLOGOWEB_SITE + NLW_MODEL_ASSET_PATH + model.substring(NLW_MODEL_PATH_PARTIAL.length, model.length) + ".nlogo"
              );
          }
        });
      } );
      // NOTE: on failure of the above, the NLW List will not be populated. Page reload necessary. -  12/5/2020 - CPB

      // Add a listener for iframe PostMessages. NLW sends one with the complete
      // width and height of the rendered model.
      window.addEventListener('message',
        function handleMessage(e) {
          // Check that the message is from where we think
          if (e.origin = NETLOGOWEB_SITE) {
            // load in the iframe, resize, and render a border

            nlwPreview = dialog.getContentElement('tab', 'nlw-preview').getElement()
            nlwPreview.setStyle('width',  (e.data.width + "px"))
            nlwPreview.setStyle('height', (e.data.height + "px"))
            nlwPreview.setStyle("border", "1px solid black")
          }
        }, false);
    },

    // Invoked when the dialog is loaded.
    onShow: function() {
      // Get the selection from the editor.
      var selection = editor.getSelection();
      // Get the element at the start of the selection.
      var element = selection.getStartElement();
      // Store it for later use if needed
      this.element = element;
      this.setupContent( this.element );
    },

    // This method is invoked once a user clicks the INSERT MODEL button, confirming the dialog.
    onOk: function() {

      var dialog = this;

      // load up the preview element
      nlwPreview = dialog.getContentElement('tab', 'nlw-preview').getElement()

      // Create our iframe
      var newElement = new CKEDITOR.dom.element( 'iframe' );
      newElement.setStyle('width',  nlwPreview.getStyle('width'));
      newElement.setStyle('height', nlwPreview.getStyle('height'));
      newElement.setAttribute('src', dialog.getContentElement('tab', 'model-picker').getValue());

      // Place it in the editor
      editor.insertElement( newElement );
    },
  };
});
