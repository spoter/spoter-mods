package components
{
    import flash.text.*;
    import flash.events.*;

    public class AMButton extends TextField
    {
        private var _tooltip: String = "";
        private static const _mouseoutimg: String = "gui/flash/AccountsManager/AM_Icon_MouseOut.png";
        private static const _mouseoverimg: String = "gui/flash/AccountsManager/AM_Icon_MouseOver.png";

        public function set tooltip(new_tooltip:String):void
        {
            _tooltip = new_tooltip;
        }

        public function AMButton()
        {
            super();
            htmlText = "<img width='39' height='39' src='img://" + _mouseoutimg + "'>";
            width = 41;
            height = 41;
            selectable = false;
            addEventListener(MouseEvent.MOUSE_OVER, onMouseOver);
            addEventListener(MouseEvent.MOUSE_OUT, onMouseOut);
        }

        public function onMouseOver(e:MouseEvent):void
        {
            htmlText = "<a href='event:#'><img width='39' height='39' src='img://" + _mouseoverimg + "'></a>";
            App.toolTipMgr.show(_tooltip);
        }

        public function onMouseOut(e:MouseEvent):void
        {
            htmlText = "<img width='39' height='39' src='img://" + _mouseoutimg + "'>";
            App.toolTipMgr.hide();
        }
    }
}
