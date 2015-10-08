README


Setting django_wysiwyg and tinymce



Set the tinymce config to the following in /python2.7/site-packages/django_wysiwyg/templates/django_wysiwyg/tinymce_advanced/includes.html

{% extends "django_wysiwyg/tinymce/includes.html" %}

{% block django_wysiwyg_editor_config %}
    var django_wysiwyg_editor_config = {
        relative_urls: false,
        custom_undo_redo_levels: 10,
        plugins: 'paste,autoresize,inlinepopups,preview,media,table',
        strict_loading_mode: true,  // for pre 3.4 releases

        width: '610px',

        theme: "advanced",
        theme_advanced_toolbar_location: 'top',
        theme_advanced_toolbar_align: 'left',
        theme_advanced_buttons1: 'bold,italic,underline,strikethrough,|,link,unlink,|,bullist,numlist,|,undo,redo,|,formatselect,|,removeformat,cleanup,code',
        theme_advanced_buttons2: 'outdent,indent,|,sub,sup,|,image,charmap,anchor,hr',
        theme_advanced_buttons3: 'preview, media,inserttable',
        theme_advanced_blockformats: 'h1,h2,h3,p',
        theme_advanced_resizing : true,
        extended_valid_elements :  'iframe[src|width|height|name|align]',
    };
{% endblock %}
