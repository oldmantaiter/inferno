def keyset_multiplier(stream, size, url, params):
    for in_dict in stream:
        for keyset_name in params.keysets.keys():
            try:
                dprime = dict(in_dict)
            except Exception as e:
                print "KEYSET Parts Error: %s" % in_dict
            else:
                dprime['_keyset'] = keyset_name
                yield dprime


def json_reader(stream, size=None, url=None, params=None):
    import ujson
    for line in stream:
        if line.find('{') != -1:
            try:
                parts = ujson.loads(line.rstrip())
                assert isinstance(parts, dict)
            except:
                # just skip bad lines
                print 'json line error: %r' % line
            else:
                yield parts


def csv_reader(stream, size=None, url=None, params=None):
    import csv
    import __builtin__

    fieldnames = getattr(params, 'csv_fields', None)
    dialect = getattr(params, 'csv_dialect', 'excel')
    delimiter = getattr(params, 'delimiter', None)

    if delimiter:
        reader = csv.reader(stream, delimiter=delimiter)
    else:
        reader = csv.reader(stream, dialect=dialect)

    done = False
    while not done:
        try:
            line = reader.next()
            if not line:
                continue
            if not fieldnames:
                fieldnames = [str(x) for x in range(len(line))]
            parts = dict(__builtin__.map(None, fieldnames, line))
            if None in parts:
                # remove extra data values
                del parts[None]
            yield parts
        except StopIteration as e:
            done = True
        except Exception as ee:
            # just skip bad lines
            print 'csv line error: %s' % ee


def dynamic_reader(stream, size=None, url=None, params=None):
    """ This reader uses parts of both json_reader and csv_reader...
        It will attempt to json_read the stream, and if that fails, it will try to csv_read it instead
        using the fieldnames/dialect/delimiter as used in the csv_reader.
        This is helpful in cases where an inferno job has more than one source tag,
        where one of them may be json encoded, while the other may be delimited by some character
    """ 
    import ujson
    import csv
    import __builtin__

    fieldnames = getattr(params, 'csv_fields', None)
    dialect = getattr(params, 'csv_dialect', 'excel')
    delimiter = getattr(params, 'delimiter', None)

    if delimiter:
        reader = csv.reader(stream, delimiter=delimiter)
    else:
        reader = csv.reader(stream, dialect=dialect)

    done = False
    for line in stream:
        if line.find('{') != -1:
            try:
                parts = ujson.loads(line.rstrip())
                assert isinstance(parts, dict)
            except:
                # just skip bad lines
                print 'json line error: %r' % line
            else:
                yield parts
        else:
            # We couldn't find '{' in the line so it is not json encoded... use csv reader!
            while not done:
                try:
                    if not line:
                        line = reader.next()
                        continue
                    if not fieldnames:
                        fieldnames = [str(x) for x in range(len(line))]
                    parts = dict(__builtin__.map(None, fieldnames, line))
                    if None in parts:
                        # remove extra data values
                        del parts[None]
                    yield parts
                except StopIteration as e:
                    done = True
                except Exception as ee:
                    # just skip bad lines
                    print 'csv line error: %s' % ee
                line = reader.next()
        if done:
            break
