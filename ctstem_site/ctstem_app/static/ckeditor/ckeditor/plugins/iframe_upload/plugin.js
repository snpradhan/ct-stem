/**
 * @license Copyright (c) 2003-2019, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or https://ckeditor.com/legal/ckeditor-oss-license
 */

'use strict';

( function() {
	CKEDITOR.plugins.add( 'iframe_upload', {
		requires: 'uploadwidget,link',
		init: function( editor ) {
			// Do not execute this paste listener if it will not be possible to upload file.
			if ( !this.isSupportedEnvironment() ) {
				return;
			}

			var fileTools = CKEDITOR.fileTools,
				uploadUrl = fileTools.getUploadUrl( editor.config );

			if ( !uploadUrl ) {
				CKEDITOR.error( 'uploadfile-config' );
				return;
			}

			fileTools.addUploadWidget( editor, 'uploadfile', {
				uploadUrl: fileTools.getUploadUrl( editor.config ),

				fileToElement: function( file ) {
					// Show a placeholder with an empty link during the upload.

               var newElement;

               if (file.type == "text/html") {
                  newElement = new CKEDITOR.dom.element( 'iframe' );
                  newElement.setAttribute('src', ' ');
                  newElement.setAttribute('width', 1000);
                  newElement.setAttribute('height', 1000);
               }
               else {
   					newElement = new CKEDITOR.dom.element( 'a' );
   					newElement.setText( file.name );
   					newElement.setAttribute( 'href', '#' );
               }
					return newElement;
				},

				onUploaded: function( upload ) {

               if (upload.file.type == "text/html") {
                  this.replaceWith( '<iframe src="' + upload.url + '" height="1000" width="1000">' +
                  "Something has gone wrong. Please reload the page." +
                  '</iframe>' );
               }

					else {
                  this.replaceWith( '<a href="' + upload.url + '" target="_blank">' + upload.fileName + '</a>' );
               }
				}
			} );
		},

		isSupportedEnvironment: function() {
			return CKEDITOR.plugins.clipboard.isFileApiSupported;
		}
	} );
} )();
