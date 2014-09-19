# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table(u'thumbnails_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'thumbnails', ['Source'])

        # Adding model 'ThumbnailMeta'
        db.create_table(u'thumbnails_thumbnailmeta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thumbnails', to=orm['thumbnails.Source'])),
            ('size', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'thumbnails', ['ThumbnailMeta'])

        # Adding unique constraint on 'ThumbnailMeta', fields ['source', 'size']
        db.create_unique(u'thumbnails_thumbnailmeta', ['source_id', 'size'])


    def backwards(self, orm):
        # Removing unique constraint on 'ThumbnailMeta', fields ['source', 'size']
        db.delete_unique(u'thumbnails_thumbnailmeta', ['source_id', 'size'])

        # Deleting model 'Source'
        db.delete_table(u'thumbnails_source')

        # Deleting model 'ThumbnailMeta'
        db.delete_table(u'thumbnails_thumbnailmeta')


    models = {
        u'thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'thumbnails.thumbnailmeta': {
            'Meta': {'unique_together': "(('source', 'size'),)", 'object_name': 'ThumbnailMeta'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': u"orm['thumbnails.Source']"})
        }
    }

    complete_apps = ['thumbnails']