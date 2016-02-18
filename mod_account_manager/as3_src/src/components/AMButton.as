package components 
{
	import flash.text.TextField;
	import flash.events.MouseEvent;

	public class AMButton extends TextField
	{
		protected var _tooltip		: String = "";
		protected var _mouseoutimg	: String = "gui/flash/AccountsManager/AM_Icon_MouseOut.png";
		protected var _mouseoverimg	: String = "gui/flash/AccountsManager/AM_Icon_MouseOver.png";

		public function set tooltip(new_tooltip : String) : void
		{
			this._tooltip = new_tooltip;
		}

		public function AMButton() 
		{
			super();
			this.htmlText = "<img width='39' height='39' src='img://" +this._mouseoutimg + "'>";
			this.width = 41;
			this.height = 41;
			this.selectable = false;
			this.addEventListener(MouseEvent.MOUSE_OVER, onMouseOver);
			this.addEventListener(MouseEvent.MOUSE_OUT, onMouseOut);
		}

		public function onMouseOver(e : MouseEvent) : void
		{
			this.htmlText = "<a href='event:#'><img width='39' height='39' src='img://" +this._mouseoverimg + "'></a>";
			App.toolTipMgr.show(this._tooltip);
		}

		public function onMouseOut(e : MouseEvent) : void
		{
			this.htmlText = "<img width='39' height='39' src='img://" +this._mouseoutimg + "'>";
			App.toolTipMgr.hide();
		}

	}

}
