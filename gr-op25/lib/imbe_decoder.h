/* -*- C++ -*- */

/*
 * Copyright 2008 Steve Glass
 * 
 * This file is part of OP25.
 * 
 * OP25 is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * OP25 is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
 * License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with OP25; see the file COPYING.  If not, write to the Free
 * Software Foundation, Inc., 51 Franklin Street, Boston, MA
 * 02110-1301, USA.
 */

#ifndef INCLUDED_IMBE_DECODER_H 
#define INCLUDED_IMBE_DECODER_H 

#include <boost/noncopyable.hpp>
#include <boost/shared_ptr.hpp>
#include <deque>
#include <vector>

typedef std::deque<float> audio_samples;
typedef std::vector<bool> voice_codeword;

typedef boost::shared_ptr<class imbe_decoder> imbe_decoder_sptr;

/**
 * imbe_decoder is the interface to the various mechanisms for
 * translating P25 voice codewords into audio samples.
 */
class imbe_decoder : public boost::noncopyable {
public:

   /**
    * imbe_decoder (virtual) constructor. The exact subclass
    * instantiated depends on some yet-to-be-decided magic.
    *
    * \return A shared_ptr to an imbe_decoder.
    */
   static imbe_decoder_sptr make();

   /**
    * imbe_decoder (virtual) destructor.
    */
   virtual ~imbe_decoder();

   /**
    * Decode the compressed IMBE audio.
    *
    * \param cw IMBE codeword (including parity check bits).
    */
   virtual void decode(const voice_codeword& cw) = 0;

   /**
    * Returns the audio_samples samples. These are mono samples at
    * 8KS/s represented as a float in the range -1.0 .. +1.0.
    *
    * \return A non-null pointer to a deque<float> of audio samples.
    */
   audio_samples *audio();

protected:

   /**
    * Construct an instance of imbe_decoder. Access is protected
    * because this is an abstract class and users should call
    * make_imbe_decoder to construct  concrete instances.
    */
   imbe_decoder();

private:

   /**
    * The audio samples produced by the IMBE decoder.
    */
   audio_samples d_audio;
   
};

#endif /* INCLUDED_IMBE_DECODER_H */
