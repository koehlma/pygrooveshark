Ext.regModel('Song', {
    fields: ['id', 'name', 'artist', 'artist_id', 'album', 'album_id', 'track', 'duration', 'popularity', 'cover']
});


Ext.application({
    name: 'FreeGroove',
    launch: function() {
        var popular = Ext.create('Ext.data.Store', {
            model: 'Song',
            proxy: {
                type: 'ajax',
                url : '/request?command=popular',
                reader: {
                    type: 'json',
                    root: 'result'
                }
            },
            autoLoad: true
        });
        
        player = Ext.get('player');
        
        var grid = Ext.create('Ext.grid.Panel', {
            store: popular,
            columns: [
                {
                    text     : 'Name',
                    sortable : true,
                    dataIndex: 'name',
                    flex: 1
                }, {
                    text     : 'Album',
                    sortable : true,
                    dataIndex: 'album',
                    flex: 1
                }, {
                    text     : 'Artist',
                    sortable : true,
                    dataIndex: 'artist',
                    flex: 1
                }
            ],
            title: 'Popular'
        });
                
        function play(grid, record, item, index, e, eopts) {
            player.dom.src = 'request?command=stream&song=' + Ext.JSON.encode(record.data)
            player.dom.load();
      	    player.dom.play();
        };
                
        /*
        function play(grid, record, item, index, e, eopts) {
            Ext.Ajax.request({
                url : 'request' , 
                params : { 
            	    command: 'streamurl',
            	    song: Ext.JSON.encode(record.data)
            	},
            	method: 'GET',
            	success: function(response) {
            	    player.dom.src = Ext.JSON.decode(response.responseText).result;
                    player.dom.load();
            	    player.dom.play();
            	},
            	failure: function ( result, request) { 
            		alert('fail'); 
        	    } 
            });
        };
        */
          
        grid.addListener('itemclick', play);
        
        var tabbar = Ext.create('Ext.tab.Panel', {
            items: [
                grid , {
                title: 'Search',
                html: 'Test...'
            }]
        });
        
        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: tabbar
        });
    }
});
