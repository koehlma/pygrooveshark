Ext.application({
    name: 'FreeGroove',
    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'border',
            items: [
                {
                    region : 'north',
                    title: 'FreeGroove',
                    html : 'Hello! Welcome to FreeGroove.',
                    height : 100,
                    width : 100
                }, {
                    region : 'center',
                    title: 'FreeGroove',
                    html : 'Hello! Welcome to FreeGroove.',
                    height : 100,
                    width : 100
                }
            ]
        });
    }
});
