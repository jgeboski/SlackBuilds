config() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  if [ ! -r $OLD ]; then
    mv $NEW $OLD
  elif [ "$(cat $OLD | md5sum)" = "$(cat $NEW | md5sum)" ]; then
    rm $NEW
  fi
}

preserve_perms() {
  NEW="$1"
  OLD="$(dirname $NEW)/$(basename $NEW .new)"
  if [ -e $OLD ]; then
    cp -a $OLD ${NEW}.incoming
    cat $NEW > ${NEW}.incoming
    mv ${NEW}.incoming $NEW
  fi
  config $NEW
}

preserve_perms etc/rc.d/rc.apache-openmeetings.new
config opt/apache-openmeetings/conf/jee-container.xml.new
config opt/apache-openmeetings/conf/jee-container-ssl.xml.new
config opt/apache-openmeetings/conf/red5.properties.new
config opt/apache-openmeetings/conf/red5-core.xml.new
config opt/apache-openmeetings/webapps/openmeetings/config.xml.new
config opt/apache-openmeetings/webapps/openmeetings/WEB-INF/classes/META-INF/persistence.xml.new
